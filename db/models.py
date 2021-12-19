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
    name = orm.StringCol(notNone=True, unique=True)
    dnevnik_id = orm.IntCol(notNone=True, unique=True)
    # Связь с другими таблицами
    timetable = orm.MultipleJoin('Timetable')


class Timetable(orm.SQLObject):
    """Таблица БД содержащая расписание уроков,
    с информацией о номере кабинета и учителе

    Args:
        date ([str]): дата события в расписании
        lesson_number ([int]): порядковый номер урока
        lesson_name ([str]): Имя урока (предмет)
        lesson_room ([int]): место проведения урока (кабинет)
        lesson_teacher ([str]): ФИО учителя, который проводит урок
        classes ([ForeignKey]): привязка к названию учебного класса
    """
    date = orm.StringCol(notNone=True)
    lesson_number = orm.IntCol(notNone=True)
    lesson_name = orm.StringCol(default=None)
    lesson_room = orm.StringCol(default=None)
    lesson_teacher = orm.StringCol(default=None)
    lesson_time = orm.StringCol(default=None)
    # Связь с другими таблицами
    classes = orm.ForeignKey('Classes')
