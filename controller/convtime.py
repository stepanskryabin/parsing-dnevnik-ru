from typing import NamedTuple
from datetime import timedelta
from datetime import date

from loguru import logger

from controller.config import DNEVNIK_RU
from controller.config import TRIMESTER


class Date(NamedTuple):
    name: str
    date: date
    str_date: str


def filtred_by_week(year: int,
                    month: int,
                    day: int,
                    deep_day: int) -> set:
    """
    Выводит список двух дат принадлежащих разным неделям.

    Даты могут быть любыми, главный критерий это обязательная принадлежность
    к разным неделям.

    Args:
        year: год начала
        month: месяц начала
        day: день начала
        deep_day: глубина (дни) на которую загружается расписание

    Returns:
        список дат, которые принадлежат только одной неделе.
        На одну неделю - одна дата.
    """

    start_date = date(year, month, day)
    list_of_day = [timedelta(day) for day in range(deep_day)]
    list_of_date = [start_date + day for day in list_of_day]

    result = []
    new_week = list_of_date[0]
    result.append(new_week)
    for d in list_of_date:
        if d.isocalendar()[1] > new_week.isocalendar()[1]:
            new_week = d
        else:
            d = new_week
        result.append(d)
    return set(result)


def date_on_week(today: date = None,
                 week: int = None) -> tuple[Date]:
    """
    Выводит список дат с понедельника по воскресенье
    используя для этого только текущую дату.

    Args:
        today: текущая дата
        week: номер недели, где 1 - текущая, 2 следующая

    Returns:
        список дат с понедельника по воскресенье
    """

    if today is None:
        TODAY = date.today()
    else:
        TODAY = today

    if week is None:
        WEEK = 1
    else:
        WEEK = week

    WEEKDAY_NAME = ("ПН",
                    "ВТ",
                    "СР",
                    "ЧТ",
                    "ПТ",
                    "СБ",
                    "ВС")
    NUMBER_LIST = [0,
                   1,
                   2,
                   3,
                   4,
                   5,
                   6]

    WEEKDAY = date.weekday(TODAY)
    FIRST_DAY = TODAY - timedelta(days=NUMBER_LIST.index(WEEKDAY))

    result = []
    if WEEK == 1:
        for day in range(7):
            date_ = FIRST_DAY + timedelta(day)
            result.append(Date(name=WEEKDAY_NAME[day],
                               date=date_,
                               str_date=str(date_)))
        return tuple(result) 
    elif WEEK == 2:
        for day in range(7):
            date_ = FIRST_DAY + timedelta(day) + timedelta(7)
            result.append(Date(name=WEEKDAY_NAME[day],
                               date=date_,
                               str_date=str(date_)))
        return tuple(result)


def convert_to_isodate(from_string: str) -> str:
    """
    Конвертирует найденный ID в дату в ISO-формате.

    Args:
        from_string: строка содержащая дату, например 'd20201101'.

    Returns:
        Возвращает дату в формате ISO, например '2020-11-01'.
    """

    var = from_string.lstrip('d')
    return date(int(var[0:4]),
                int(var[4:6]),
                int(var[6:8])).isoformat()


def get_trimester(request_date: date) -> int:
    """
    Определяет номер триместра.

    Args:
        request_date: дата

    Returns:
        Возвращает номер триместра в системе dnevnik.ru
        Номера всех триместров задаются в config.ini
    """

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
        logger.error(''.join(("Ошибка в определении триместра. ",
                              "Использован номер первого триместра")))
        return number_of_trimester[1]
