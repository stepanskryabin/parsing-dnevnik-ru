from collections import namedtuple
from datetime import timedelta, date


def filtred_by_week(year: int,
                    month: int,
                    day: int,
                    deep_day: int) -> tuple:
    """Функция выдаёт список двух дат принадлежащих разным неделям

    Args:
        year (int): год начала
        month (int): месяц начала
        day (int): день начала
        deep_day (int): глубина (дни) на которую загружается расписание

    Returns:
        tuple: список дат, которые принадлежат только одной неделе.
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
    return tuple(result)


def date_on_week(today=None,
                 week=None) -> tuple:
    """Функция выводит список дат с понедельника по воскресенье
    используя для этого только текущую дату

    Args:
        today (date): текущая дата
        week (int): номер недели, где 1 - текущая, 2 следующая

    Returns:
        tuple: список дат с понедельника по воскресенье
    """
    if today is None:
        TODAY = date.today()
    else:
        TODAY = today
    if week is None:
        WEEK = 1
    else:
        WEEK = week
    Date = namedtuple("Date", ["name",
                               "date",
                               "str_date"])
    WEEKDAY_NAME= ("ПН",
                   "ВТ",
                   "СР",
                   "ЧТ",
                   "ПТ",
                   "СБ",
                   "ВС")
    WEEKDAY = date.weekday(TODAY)
    a = [0,
         1,
         2,
         3,
         4,
         5,
         6]
    FIRST_DAY = TODAY - timedelta(days=a.index(WEEKDAY))
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
