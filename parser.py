import configparser
from datetime import timedelta, date

from bs4 import BeautifulSoup
from selenium import webdriver
# import sqlobject as orm

# from .models import db

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
# ************** END **********************************

add_logging(LOGGING.getint('level'))


def get_info(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', id='editor')
    tbody = table.find('tbody')
    tr = tbody.find_all('tr')
    table_head = []
    text = []
    teacher = []
    room = []

    # Отбираем заголовки таблицы с названием дня
    for item in tr:
        th = item.find_all('th')
        for item in th:
            head = item.find('a')
            if head is None:
                continue
            else:
                table_head.append(head.text)

    # Отбираем ячейки таблицы с номером урока
    for item in tr:
        td = item.find_all('td')
        for item in td:
            lesson_number = item.find('strong')
            if lesson_number is None:
                pass
            else:
                lesson_number = lesson_number.text
                print("lesson_number: ", lesson_number)
            # Отбираем название уроков
            lesson = item.find('div', class_='dL')
            if lesson is None:
                pass
            else:
                lesson = lesson.find('a').get('title')
                print('Lesson: ', lesson)

    # Отбираем ячейки с именем учителя
    for item in tr:
        td = item.find_all('td')
        for item in td:
            div = item.find_all('div')
            for item in div:
                p1 = item.find('p')
                teacher.append(p1)
                p2 = item.findNext('p')
                room.append(p2)
    print(table_head)
    print(text)
    return


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
        logger.debug("Информация о классах не найдена")
    else:
        first_li = ul.find_all('li')
        for item in first_li:
            second_li = item.find_all('li')
            for item in second_li:
                url: str = item.find('a').get('href')
                if url is None:
                    class_name = None
                    logger.debug('Ссылка на учебный класс не найдена')
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
            result = number_of_trimester[1]
        elif first_trimester < request_date <= second_trimester:
            result = number_of_trimester[2]
        elif second_trimester < request_date <= third_trimester:
            result = number_of_trimester[3]
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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=OTHER.get('browser_driver'),
                               options=options)
    # Таймаут чтобы браузер загрузился
    browser.implicitly_wait(10)
    browser.get(url)
    browser.find_element_by_name('login').clear()
    browser.find_element_by_name('login').send_keys(USER.get('login'))
    browser.find_element_by_name('password').clear()
    browser.find_element_by_name('password').send_keys(USER.get('password'))
    browser.find_element_by_xpath("//input[@type='submit'][@data-test-id='login-button']").click()
    # Таймаут чтобы произошел переход в личный кабинет
    browser.implicitly_wait(10)
    # Переходим на страницу школьных расписаний с актуальным годом
    browser.get(''.join([f'{DNEVNIK_RU.get("schedules_url")}',
                         f'?school={PARAMETERS.get("school")}',
                         f'&tab=groups&year={PARAMETERS.get("year")}']))
    browser.implicitly_wait(10)
    # Парсим ссылки на все классы
    tuple_of_classes: tuple[tuple] = get_classes(browser.page_source)
    logger.debug(f"Все классы: {tuple_of_classes}")
    # Подготавливаем кортеж из всех ссылок на расписание
    schedules = get_schedules(tuple_of_classes=tuple_of_classes,
                              start_year=PARAMETERS.getint('year'),
                              start_month=PARAMETERS.getint('month'),
                              start_day=PARAMETERS.getint('day'),
                              deep_day=PARAMETERS.getint('deep_day'))
    # Обходим кортеж ссылок и получаем html для обработки
    for schedule in schedules:
        browser.get(schedule)
        browser.implicitly_wait(10)
        raw_html = browser.page_source
        logger.debug("Получен raw html")
        get_info(raw_html)
    return


if __name__ == "__main__":
    main(DNEVNIK_RU.get('login_url'))
