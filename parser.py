import configparser
from datetime import timedelta, date
from os import name as OS_NAME

from bs4 import BeautifulSoup
from selenium import webdriver
import sqlobject as orm

from models import db

# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging
logging.disable()
# ************** Logging end *************************

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
USER = config['USER']
PARAMETERS = config['PARAMETERS']
OTHER = config['OTHER']
LOGGING = config['LOGGING']
DNEVNIK_RU = config['DNEVNIK_RU']
TRIMESTER = config['TRIMESTER']
DB = config['DATABASE']
# ************** END **********************************

add_logging(LOGGING.getint('level'))


try:
    connect = orm.connectionForURI(DB.get('uri'))
    logger.debug(f"Читаем адрес БД: {DB.get('uri')}")
except Exception as ERROR:
    logger.exception(f'Ошибка подключения к БД: {ERROR}')
else:
    orm.sqlhub.processConnection = connect
    logger.debug('Подключение к БД выполнено успешно')


def get_lessons(html) -> tuple[tuple]:
    """Функция парсит полученный HTML и записывает информацию в кортеж.
    Записывается: наименование класса, ID класса, дата в формате ISO,
    номер урока, название урока, имя учителя, номер кабинета, время урока.

    Args:
        html ([type]): raw HTML

    Returns:
        [tuple]: кортеж с вложенными кортежами
    """
    def convert_to_isodate(string: str) -> str:
        """Функция конвертирует найденный ID в дату
        в ISO-формате

        Args:
            string (str): строка содержащая дату, например 'd20201101'

        Returns:
            [str]: возвращает дату в формате ISO, например '2020-11-01'
        """
        var: str = string.lstrip('d')
        result = date(int(var[0:4]), int(var[4:6]), int(var[6:8]))
        return result.isoformat()

    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', id='content')
    schedules_classes: str = content.find('a', class_='blue')
    logger.debug("Найдено имя учебного класса")
    classes_group_id: str = schedules_classes.get('href')
    logger.debug(f"Получена ссылка с ID класса: {classes_group_id}")
    dnevnik_ru_id: int = int(classes_group_id.rsplit(sep='=')[1])
    logger.debug(f"Получен ID класса: {dnevnik_ru_id}")
    tbody = content.find('tbody')
    all_th = tbody.find_all('th')
    logger.debug("Найдены все заголовки таблицы с расписанием")
    all_tr = tbody.find_all('tr')
    logger.debug("Найдены все строки таблицы с расписанием")
    #
    # Первый цикл: находим все наименования дней недели
    schedule_dates = []
    for item in all_th:
        schedules_date_id: str = item.get('id')
        if schedules_date_id is None:
            logger.debug("Отсутствует ID")
            continue
        else:
            logger.debug(f"Найдены ID: {schedules_date_id}")
            schedule_dates.append(schedules_date_id)
    schedule_dates = tuple(schedule_dates)
    #
    # Второй цикл: находим номера уроков
    lesson_numbers = []
    for item in all_tr:
        l_number: str = item.find('td', class_='wDS')
        logger.debug("Найдены ячейки таблицы с номером урока")
        if l_number is None:
            logger.debug("Номер урока отсутствует")
            continue
        else:
            lesson_number: int = int(l_number.strong.text)
            logger.debug("Номер урока найден")
            lesson_numbers.append(lesson_number)
    lesson_numbers = tuple(lesson_numbers)
    #
    # Третий цикл: находим название урока, учителя, время и кабинет
    # и кладём это в едтиный кортеж с уже включенными: датой урока и
    # номером урока
    schedules = []
    for item in all_tr:
        for schedules_date_id in schedule_dates:
            for lesson_number in lesson_numbers:
                lesson_info = item.find('td',
                                        id=f'{schedules_date_id}_{lesson_number}')
                if lesson_info is None:
                    continue
                else:
                    logger.debug("Найдена ячейка расписания")
                    lesson_name: str = lesson_info.find('a', class_='aL')
                if lesson_name is None:
                    lesson_name = 'Урок отсутствует'
                else:
                    lesson_name = lesson_name.get('title')
                if lesson_info.div.p is None:
                    continue
                else:
                    first_p = lesson_info.div.p
                    _ = first_p.get('title')
                    second_p = first_p.find_next('p')
                    lesson_teacher: str = second_p.text
                    third_p = second_p.find_next('p')
                    lesson_time: str = third_p.text
                    fourth_p = third_p.find_next('p')
                    lesson_room: int = int(fourth_p.text)
                    logger.debug("Собираем информацию об уроке")
                    result = (schedules_classes.encode(encoding='utf-8'),
                              dnevnik_ru_id,
                              convert_to_isodate(schedules_date_id),
                              lesson_number,
                              lesson_name.encode(encoding='utf-8'),
                              lesson_teacher.encode(encoding='utf-8'),
                              lesson_time,
                              lesson_room)
                    schedules.append(result)
    schedules = tuple(schedules)
    return schedules


def write_db(lesson: tuple[tuple]) -> None:
    dbquery = db.Classes.selectBy(name=lesson[0],
                                  dnevnik_ru_id=lesson[1])
    if dbquery.count == 0:
        new_class = db.Classes(name=lesson[0],
                               dnevnik_ru_id=lesson[1])
    elif dbquery.count == 1:
        new_class = dbquery
    else:
        logger.debug("Записей больше одной")
        pass
    try:
        db.Timetable(date=lesson[2],
                     lesson_number=lesson[3],
                     lesson_name=lesson[4],
                     lesson_room=lesson[7],
                     lesson_teacher=lesson[5],
                     lesson_time=lesson[6],
                     classes=new_class)
        logger.info('Информация об уроке записана в БД')
        return
    except Exception as ERROR:
        logger.exception(f"Запис в БД неудачна: {ERROR}")
        return


def get_classes(html) -> tuple[tuple]:
    """Функция находит наименования учебных классов url-ссылки на них
    и их ID.

    Args:
        html ([type]): raw html

    Returns:
        tuple[tuple]: кортеж со вложенным кортежем первым элементом которого
        является учебный класс, вторым элементом ссылка, а третьим элементов ID класса.
    """
    soup = BeautifulSoup(html, 'lxml')
    ul = soup.find('ul', class_='classes')
    data = []
    if ul is None:
        logger.error("Информация о классах не найдена")
    else:
        first_li = ul.find_all('li')
        for item in first_li:
            second_li = item.find_all('li')
            for item in second_li:
                url: str = item.find('a').get('href')
                if url is None:
                    class_name = None
                    class_id = None
                    logger.error('Ссылка на учебный класс не найдена')
                else:
                    # разделяем сылку посредством разделителя "=" на список
                    # содержащий три объекта, где последний объект
                    # ID учебного класса
                    class_id = url.rsplit(sep="=")[2]
                    class_name: str = item.a.text
                    element: tuple = (class_name, url, class_id)
                    data.append(element)
        logger.success("Поиск информации о классах и ссылках выполнен успешно")
    return tuple(data)


def get_schedules(tuple_of_classes: tuple[tuple],
                  start_year: int,
                  start_month: int,
                  start_day: int,
                  deep_day: int) -> tuple:
    """Функция генерирует кортеж с ссылками на расписание
    уроков от заданной даты и на заданную глубину

    Args:
        tuple_of_classes (tuple[tuple]): кортеж содержащий имя учебного
        класса, ссылку на его расписание и ID. Используется только
        второй элемент кортежа.
        start_year (int): год начала загрузки расписания
        start_month (int): месяц  начала загрузки расписания
        start_day (int): день  начала загрузки расписания
        deep_day (int): глубина (дни) на которую загружается расписание

    Returns:
        tuple: кортеж с ссылками на расписание для всех классов
    """
    def filtred_by_week(tuple_of_date: tuple) -> tuple:
        result = []
        new_week = tuple_of_date[0]
        result.append(new_week)
        for d in tuple_of_date:
            if d.isocalendar()[1] > new_week.isocalendar()[1]:
                new_week = d
                logger.debug(f"Номер недели: {new_week}")
                result.append(d)
            else:
                logger.debug("Номер недели меньше начального")
        return tuple(result)

    def get_trimester(request_date) -> int:
        logger.debug(f"Дата запроса: {request_date}")
        number_of_trimester = (DNEVNIK_RU.getint('1trimester'),
                               DNEVNIK_RU.getint('2trimester'),
                               DNEVNIK_RU.getint('3trimester'))
        first_trimester = date.fromisoformat(TRIMESTER.get('first'))
        second_trimester = date.fromisoformat(TRIMESTER.get('second'))
        third_trimester = date.fromisoformat(TRIMESTER.get('third'))
        if request_date <= first_trimester:
            result = number_of_trimester[0]
        elif first_trimester < request_date <= second_trimester:
            result = number_of_trimester[1]
        elif second_trimester < request_date <= third_trimester:
            result = number_of_trimester[2]
        else:
            logger.error(' '.join("Ошибка в определении триместра.",
                                  "Использован номер первого триместра"))
            result = number_of_trimester[1]
        return result

    start_date = date(start_year, start_month, start_day)
    list_of_day = [timedelta(day) for day in range(deep_day + 1)]
    list_of_date = [start_date + day for day in list_of_day]
    date_filtred = filtred_by_week(list_of_date)
    logger.debug(f"Список дат: {list_of_date}")
    logger.debug(f"Список классов: {tuple_of_classes}")
    result = []

    for item in tuple_of_classes:
        # в кортеже list_of_classes находится вложенный кортеж из двух
        # элементов: первый элемент название учебного класса,
        #            второй элемент ссылка на его расписание
        link_to_class = item[1]
        # FIXME после тестов убрать
        link_to_class = 'https://schools.dnevnik.ru/schedules/view.aspx?school=10509&group=1849711203825070779'
        logger.debug(f"ИСПОЛЬЗУЕТСЯ ОДИН КЛАСС: {link_to_class}")
        for d in date_filtred:
            schedules = ''.join([f'{link_to_class}',
                                 f'&period={get_trimester(d)}',
                                 f'&year={d.year}',
                                 f'&month={d.month}',
                                 f'&day={d.day}'])
            result.append(schedules)
    logger.debug(f"Список ссылок на расписание: {result}")
    return tuple(result)


def main(url: str):
    if OS_NAME == 'nt':
        executable = "".join((".\\", OTHER.get('browser_driver'), ".exe"))
    elif OS_NAME == 'posix':
        executable = "".join((".\\", OTHER.get('browser_driver')))
    # Настраиваем и запускаем браузер
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=executable)
    # Выставляем таймаут, чтобы браузер ждал 10 сек
    # после выполнения каждого действия
    browser.implicitly_wait(10)
    logger.debug('Браузер загрузился')
    browser.get(url)
    browser.find_element_by_name('login').clear()
    browser.find_element_by_name('login').send_keys(USER.get('login'))
    browser.find_element_by_name('password').clear()
    browser.find_element_by_name('password').send_keys(USER.get('password'))
    browser.find_element_by_xpath("//input[@type='submit'][@data-test-id='login-button']").click()
    logger.debug("Переход в ЛК")
    # Переходим на страницу школьных расписаний с актуальным годом
    browser.get(''.join([f'{DNEVNIK_RU.get("schedules_url")}',
                         f'?school={PARAMETERS.get("school")}',
                         f'&tab=groups&year={PARAMETERS.get("year")}']))
    logger.debug("Переход на страницу с расписаниями")
    # Парсим ссылки на все классы
    tuple_of_classes: tuple[tuple] = get_classes(browser.page_source)
    logger.debug(f"Все классы спарсены: {tuple_of_classes}")
    # Подготавливаем кортеж из всех ссылок на расписание
    schedules = get_schedules(tuple_of_classes=tuple_of_classes,
                              start_year=PARAMETERS.getint('year'),
                              start_month=PARAMETERS.getint('month'),
                              start_day=PARAMETERS.getint('day'),
                              deep_day=PARAMETERS.getint('deep_day'))
    logger.debug("Кортеж из ссылок на расписание сформирован")
    # Обходим кортеж ссылок и получаем html для обработки
    for schedule in schedules:
        browser.get(schedule)
        raw_html = browser.page_source
        logger.debug("Получен raw html для обработки")
        lessons = get_lessons(raw_html)
        for lesson in lessons:
            write_db(lesson)
    return


if __name__ == "__main__":
    main(DNEVNIK_RU.get('login_url'))
