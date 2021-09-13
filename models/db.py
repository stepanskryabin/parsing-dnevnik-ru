import sqlobject as orm


class Classes(orm.SQLObject):
    """Таблица БД содержащая имена классов и их
    ID в системе dnevnik.ru

    Args:
        name ([str]): имя учебного класса
        dnevnik_ru_id ([str]): ID-номер учебного класса
        в системе dnevnik.ru
        timetable ([MultipleJoin]): привязка к записи содержащей расписание
    """
    name = orm.StringCol(notNone=True)
    dnevnik_ru_id = orm.IntCol()
    # Связь с другими таблицами
    timetable = orm.MultipleJoin('Timetable')


class Timetable(orm.SQLObject):
    """Таблица БД содержащая расписание уроков,
    с информацией о номере кабинета и учителе

    Args:
        date ([Date]): дата события в расписании
        dnevnik_ru_date ([str]): дата как в сервисе dnevnik.ru
        lesson_number ([int]): порядковый номер урока
        lesson_name ([str]): Имя урока (предмет)
        lesson_room ([int]): место проведения урока (кабинет)
        lesson_teacher ([str]): ФИО учителя, который проводит урок
        classes ([ForeignKey]): привязка к названию учебного класса
    """
    date = orm.StringCol()
    lesson_number = orm.IntCol()
    lesson_name = orm.StringCol()
    lesson_room = orm.IntCol()
    lesson_teacher = orm.StringCol()
    lesson_time = orm.StringCol()
    # Связь с другими таблицами
    classes = orm.ForeignKey('Classes')
