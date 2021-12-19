from datetime import date
from os import name as OS_NAME
from collections import namedtuple

from bs4 import BeautifulSoup
from selenium import webdriver

from db import dbhandler
from controller import convtime
from controller.config import LOGGING
from controller.config import DNEVNIK_RU
from controller.config import TRIMESTER
from controller.config import OTHER
from controller.config import PARAMETERS
from controller.config import USER
from controller.config import DB


# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging
logging.disable()
# ************** Logging end *************************


add_logging(LOGGING.getint('level'))

TODAY = date.today()

db = dbhandler.DBHandler(DB.get('uri'))
db.delete()
db.create()


def get_lessons(html) -> tuple[namedtuple] | str:
    """Функция парсит полученный HTML и записывает информацию в кортеж.
    Записывается: наименование класса, ID класса, дата в формате ISO,
    номер урока, название урока, имя учителя, номер кабинета, время урока.

    Args:
        html ([type]): raw HTML

    Returns:
        [tuple]: кортеж с вложенными именованными кортежами
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

    schedules_classes = soup.find('a', class_='blue')
    logger.debug("Найдено имя учебного класса")
    classes_group_id = schedules_classes.get('href')
    logger.debug(f"Получена ссылка с ID класса: {classes_group_id}")
    dnevnik_id = int(classes_group_id.rsplit(sep='=')[1])
    logger.debug(f"Получен ID класса: {dnevnik_id}")

    if soup.find('tbody') is None:
        return 'Error'

    all_th = soup.find('tbody').find_all('th')
    logger.debug("Найдены все заголовки таблицы с расписанием")
    all_tr = soup.find('tbody').find_all('tr')
    logger.debug("Найдены все строки таблицы с расписанием")

    # Находим все ID дат в расписании
    schedule_dates = [i.get('id') for i in all_th if i.get('id') is not None]

    # Находим номера уроков
    lesson_numbers = []
    for item in all_tr:
        lesson_number = item.find('td', class_='wDS')
        if lesson_number is None:
            logger.debug("Номер урока отсутствует")
            continue
        else:
            lesson_numbers.append(int(lesson_number.strong.text))
    lesson_numbers = tuple(lesson_numbers)

    # Находим название урока, учителя, время и кабинет
    # и кладём это в единый кортеж с уже включенными: датой урока и
    # номером урока
    lessons = []
    Schedules = namedtuple('Schedules', ["classes_name",
                                         "dnevnik_id",
                                         "date",
                                         "lesson_number",
                                         "lesson_name",
                                         "lesson_room",
                                         "lesson_teacher",
                                         "lesson_time"])
    for item in all_tr:
        for schedules_date in schedule_dates:
            for lesson_number in lesson_numbers:
                lesson_info = item.find('td',
                                        id=f'{schedules_date}_{lesson_number}')
                # logger.debug(f"LESSON INFO1: {lesson_info}")
                if lesson_info is None:
                    # logger.debug(f"LESSON INFO2: {lesson_info}")
                    continue
                else:
                    all_div = lesson_info.find_all('div')
                    # logger.debug(f"ALL DIV: {all_div}")
                    for div in all_div:
                        div_class = div.get('class')
                        if div_class == ['popup', 'shadow']:
                            # logger.debug(f"DIV GET1: {div_class}")
                            continue
                        elif div_class == ["dL"]:
                            # logger.debug(f"DIV GET2: {div_class}")
                            lesson_name = div.find('a', class_='aL').get('title')
                            # logger.debug(f"LESSON NAME1: {lesson_name}")
                            first_p = div.p
                            _ = first_p.get('title')
                            second_p = first_p.find_next('p')
                            lesson_teacher: str = second_p.text
                            third_p = second_p.find_next('p')
                            lesson_time: str = third_p.text
                            fourth_p = third_p.find_next('p')
                            lesson_room: str = fourth_p.text
                        elif div_class == ["dLE"]:
                            # logger.debug(f"DIV GET3: {div_class}")
                            lesson_name = None
                            lesson_room = None
                            lesson_teacher = None
                            lesson_time = None
                        result = Schedules(classes_name=schedules_classes.text,
                                           dnevnik_id=dnevnik_id,
                                           date=convert_to_isodate(schedules_date),
                                           lesson_number=lesson_number,
                                           lesson_name=lesson_name,
                                           lesson_room=lesson_room,
                                           lesson_teacher=lesson_teacher,
                                           lesson_time=lesson_time)
                        lessons.append(result)

    logger.debug("Кортеж с расписанием сформирован")
    return tuple(lessons)


def write_db(lesson: tuple[namedtuple]) -> str:
    """Функция записи данных в БД.

    Args:
        lesson (tuple[namedtuple]): [description]
    """
    logger.debug(f'Кортеж для записи: {lesson}')
    try:
        db.add_new_timetable(name=lesson.classes_name,
                             dnevnik_id=lesson.dnevnik_id,
                             date=lesson.date,
                             lesson_number=lesson.lesson_number,
                             lesson_name=lesson.lesson_name,
                             lesson_room=lesson.lesson_room,
                             lesson_teacher=lesson.lesson_teacher,
                             lesson_time=lesson.lesson_time)
        return "Ok"
    except Exception as ERROR:
        logger.exception(f"Запись в БД неудачна: {ERROR}")
        return "Error"


def get_classes(html) -> tuple[namedtuple]:
    """Функция находит наименования учебных классов, url-ссылки на них
    и их ID.

    Args:
        html ([type]): raw html

    Returns:
        tuple[tuple]: кортеж со вложенным кортежем первым элементом которого
        является учебный класс, вторым элементом ссылка, а третьим элементов
        ID класса.
    """
    soup = BeautifulSoup(html, 'lxml')
    ul = soup.find('ul', class_='classes')
    data = []
    Classes = namedtuple('Classes', ["class_name",
                                     "url",
                                     "class_id"])
    if ul is None:
        logger.error("Информация о классах не найдена")
    else:
        first_li = ul.find_all('li')
        for first_item in first_li:
            second_li = first_item.find_all('li')
            for second_item in second_li:
                url = second_item.find('a').get('href')
                if url is None:
                    class_name = None
                    class_id = None
                    logger.error('Ссылка на учебный класс не найдена')
                else:
                    # разделяем ссылку посредством разделителя "=" на список
                    # содержащий три объекта, где последний объект
                    # ID учебного класса
                    class_id = url.rsplit(sep="=")[2]
                    class_name = second_item.a.text
                    result = Classes(class_name=class_name,
                                     url=url,
                                     class_id=class_id)
                    data.append(result)
        logger.success("Поиск информации о классах и ссылках выполнен успешно")
    return tuple(data)


def get_schedules(tuple_of_classes: tuple[namedtuple],
                  start_year: int,
                  start_month: int,
                  start_day: int,
                  deep_day: int) -> set | str:
    """Функция генерирует кортеж ссылок на расписание
    уроков от заданной даты и на заданную глубину

    Args:
        tuple_of_classes (tuple[namedtuple]): кортеж содержащий именованный
        кортеж (имя учебного класса, ссылку на его расписание и ID).
        Используется только второй элемент именованного кортежа.
        start_year (int): год начала загрузки расписания
        start_month (int): месяц начала загрузки расписания
        start_day (int): день начала загрузки расписания
        deep_day (int): глубина (дни) на которую загружается расписание

    Returns:
        tuple: кортеж ссылок на расписание для всех классов
    """

    def get_trimester(request_date) -> int:
        number_of_trimester = (DNEVNIK_RU.getint('1trimester'),
                               DNEVNIK_RU.getint('2trimester'),
                               DNEVNIK_RU.getint('3trimester'))
        first_trimester = date.fromisoformat(TRIMESTER.get('first'))
        second_trimester = date.fromisoformat(TRIMESTER.get('second'))
        third_trimester = date.fromisoformat(TRIMESTER.get('third'))
        if request_date <= first_trimester:
            return number_of_trimester[0]
        elif first_trimester < request_date <= second_trimester:
            return number_of_trimester[1]
        elif second_trimester < request_date <= third_trimester:
            return number_of_trimester[2]
        else:
            logger.error(' '.join("Ошибка в определении триместра.",
                                  "Использован номер первого триместра"))
            return number_of_trimester[1]

    date_filtered = convtime.filtred_by_week(start_year,
                                             start_month,
                                             start_day,
                                             deep_day)

    result = []
    if tuple_of_classes is None:
        return 'Error'
    else:
        for item in tuple_of_classes:
            # в кортеже list_of_classes находится вложенный именованный
            # кортеж из трёх элементов: название учебного класса,
            # cсылка на расписание, ID в системе dnevnikru
            for d in date_filtered:
                schedules = ''.join([f'{item.url}',
                                     f'&period={get_trimester(d)}',
                                     f'&year={d.year}',
                                     f'&month={d.month}',
                                     f'&day={d.day}'])
                result.append(schedules)
        logger.debug(f"Список ссылок на расписание: {tuple_of_classes}")
        return set(result)


def main(url: str) -> bool:
    logger.success("Парсер запущен")
    if OS_NAME == 'nt':
        executable = "".join((".\\", OTHER.get('browser_driver'), ".exe"))
    elif OS_NAME == 'posix':
        executable = "".join(("./", OTHER.get('browser_driver')))
    logger.debug(f"Определяем тип OS: {OS_NAME}")
    # Настраиваем и запускаем браузер
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(executable_path=executable,
                               options=options)
    # Выставляем таймаут ожидания = 10 сек
    # после выполнения каждого действия
    browser.implicitly_wait(10)
    logger.debug('Браузер загрузился')
    browser.get(url)
    browser.find_element_by_name('login').clear()
    browser.find_element_by_name('login').send_keys(USER.get('login'))
    browser.find_element_by_name('password').clear()
    browser.find_element_by_name('password').send_keys(USER.get('password'))
    browser.find_element_by_xpath("//input[@type='submit'][@data-test-id='login-button']").click()
    browser.get(DNEVNIK_RU.get('base_url'))
    logger.debug("Переход в ЛК")
    # Переходим на страницу школьных расписаний с актуальным годом
    browser.get(''.join([f'{DNEVNIK_RU.get("schedules_url")}',
                         f'?school={PARAMETERS.get("school")}',
                         f'&tab=groups&year={TODAY.year}']))
    logger.debug("Переход на страницу с расписаниями")
    # Парсим ссылки на все классы
    tuple_of_classes = get_classes(browser.page_source)
    logger.debug(f"Все классы спарсены: {tuple_of_classes}")
    # Подготавливаем кортеж из всех ссылок на расписание
    schedules = get_schedules(tuple_of_classes=tuple_of_classes,
                              start_year=TODAY.year,
                              start_month=TODAY.month,
                              start_day=TODAY.day,
                              deep_day=PARAMETERS.getint('deep_day'))
    if schedules == 'Error':
        logger.error("Кортеж с ссылками на расписание пустой")
        return True
    logger.debug(f"Кортеж из ссылок на расписание сформирован {schedules}")
    # Обходим кортеж ссылок и получаем html для обработки
    for schedule in schedules:
        browser.get(schedule)
        lessons = get_lessons(browser.page_source)
        if lessons == "Error":
            logger.error("Отсутствует расписание занятий")
            continue
        for lesson in lessons:
            status = write_db(lesson)
            logger.debug(f"Попытка записи данных в БД - результат: {status}")
    logger.success("База расписаний обновлена")
    browser.quit()
    return True


if __name__ == "__main__":
    run = main(DNEVNIK_RU.get('login_url'))
    if run:
        exit()
