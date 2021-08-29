import configparser
from datetime import timedelta, date

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
    logger.debug(f"Читаем адрес БДЖ {DB.get('uri')}")
except Exception as ERROR:
    logger.exception(f'Ошибка подключения к БД: {ERROR}')
else:
    orm.sqlhub.processConnection = connect
    logger.debug('Подключение к БД выполнено успешно')


def get_info(html):
    """Функция парсит полученный HTML и записывает информацию в БД.
    Записывается: дата, дата в текстовом формате, номер урока, название урока,
    учитель, номер кабинета, время урока

    Args:
        html ([type]): raw HTML

    Returns:
        [type]:
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
    schedules_classes = content.find('a', class_='blue')
    logger.debug("Найдено имя учебного класса")
    classes_group_id: str = schedules_classes.get('href')
    logger.debug(f"Получена ссылка в которой есть ID класса: {classes_group_id}")
    dnevnik_ru_id = classes_group_id.rsplit(sep='=')[1]
    logger.debug(f"Получен ID класса: {dnevnik_ru_id}")
    new_classes = db.Classes(name=schedules_classes.text,
                             dnevnik_ru_id=dnevnik_ru_id)
    logger.debug("Найдены таблицы с расписанием")
    tbody = content.find('tbody')
    all_th = tbody.find_all('th')
    logger.debug("Найдены все заголовки таблицы с расписанием")
    all_tr = tbody.find_all('tr')
    logger.debug("Найдены все строки таблицы с расписанием")
    for item in all_th:
        schedules_date_id = item.get('id')
        if schedules_date_id is None:
            continue
        else:
            print(schedules_date_id)
            logger.debug(f"Найдены все ID: {schedules_date_id}")
            schedules_date = convert_to_isodate(schedules_date_id)
            text_date = item.find('a', alt="")
            logger.debug("Найдены заголовки таблицы с датой и названием дня")
            if text_date is None:
                logger.debug("Отсутствует название дня")
                continue
            else:
                text_date = text_date.text
                for item in all_tr:
                    lesson_number = item.find('td', class_='wDS')
                    logger.debug("Найдены ячейки таблицы с номером урока")
                    if lesson_number is None:
                        logger.debug("Номер урока отсутствует")
                        continue
                    else:
                        lesson_number = int(lesson_number.strong.text)
                        lesson_info = item.find('td', id=f'{schedules_date_id}_{lesson_number}')
                        p = lesson_info.p
                        logger.debug("Найдены все ячейки столбца с ID урока")
                        lesson_name = lesson_info.find('a', class_='aL')
                        if lesson_name is None:
                            lesson_name = 'Урок отсутствует'
                        else:
                            lesson_name = lesson_name.get('title')
                        if lesson_info.p is None:
                            continue
                        else:
                            _ = p.get('title')
                            lesson_teacher = p.find_next('p')
                            lesson_time = lesson_teacher.find_next('p')
                            lesson_room = lesson_time.find_next('p')
                        logger.debug("Собираем информацию об уроке и пишем в БД")
                        try:
                            db.Timetable(date=schedules_date,
                                         dnevnik_ru_date=text_date,
                                         lesson_number=lesson_number,
                                         lesson_name=lesson_name,
                                         lesson_room=int(lesson_room.text),
                                         lesson_teacher=lesson_teacher.text,
                                         lesson_time=lesson_time.text,
                                         classes=new_classes)
                        except Exception as ERROR:
                            logger.exception(f"Запис в БД неудачна: {ERROR}")
        return print('КОНЕЦ')


def get_classes(html) -> tuple[tuple]:
    """Функция находит наименования учебных классов и url-ссылки на них

    Args:
        html ([type]): [description]

    Returns:
        tuple[tuple]: кортеж со вложенным кортежем первым элементом которого
        является учебный класс, а вторым элементом ссылка
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
                    logger.error('Ссылка на учебный класс не найдена')
                else:
                    class_name: str = item.a.text
                    element: tuple = (class_name, url)
                    data.append(element)
        logger.success("Поиск информации о классах и ссылках выполнен успешно")
    return tuple(data)


def get_schedules(tuple_of_classes: tuple[tuple],
                  start_year: int,
                  start_month: int,
                  start_day: int,
                  deep_day: int) -> tuple:

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
    tuple_of_day = [timedelta(day) for day in range(deep_day + 1)]
    tuple_of_date = [start_date + day for day in tuple_of_day]
    date_filtred = filtred_by_week(tuple_of_date)
    logger.debug(f"Список дат: {tuple_of_date}")
    logger.debug(f"Список классов: {tuple_of_classes}")
    result = []

    for item in tuple_of_classes:
        # в кортеже list_of_classes находится вложенный кортеж из двух
        # элементов: первый элемент название учебного класса,
        #            второй элемент ссылка на его расписание
        link_to_class = item[1]
        # FIXME после тестов убрать
        link_to_class = 'https://schools.dnevnik.ru/schedules/view.aspx?school=10509&group=1712390980428985547'
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
    # Настраиваем и запускаем браузер
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=OTHER.get('browser_driver'))
    # Таймаут чтобы браузер загрузился
    browser.implicitly_wait(10)
    logger.debug('Браузер загрузился')
    browser.get(url)
    browser.find_element_by_name('login').clear()
    browser.find_element_by_name('login').send_keys(USER.get('login'))
    browser.find_element_by_name('password').clear()
    browser.find_element_by_name('password').send_keys(USER.get('password'))
    browser.find_element_by_xpath("//input[@type='submit'][@data-test-id='login-button']").click()
    # Таймаут чтобы произошел переход в личный кабинет
    browser.implicitly_wait(10)
    logger.debug("Переход в ЛК")
    # Переходим на страницу школьных расписаний с актуальным годом
    browser.get(''.join([f'{DNEVNIK_RU.get("schedules_url")}',
                         f'?school={PARAMETERS.get("school")}',
                         f'&tab=groups&year={PARAMETERS.get("year")}']))
    browser.implicitly_wait(10)
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
        browser.implicitly_wait(10)
        raw_html = browser.page_source
        logger.debug("Получен raw html для обработки")
        get_info(raw_html)
    return


if __name__ == "__main__":
    main(DNEVNIK_RU.get('login_url'))
