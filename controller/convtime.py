from datetime import timedelta, date


def filtred_by_week(year: int,
                    month: int,
                    day: int,
                    deep_day: int) -> tuple:
    """Функция выдаёт список двух дат принадлежащие разным неделям

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
