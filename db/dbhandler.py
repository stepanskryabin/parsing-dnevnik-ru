import sqlite3


class DBHandler:
    def __init__(self,
                 uri: str = "sqlite:/:memory:") -> None:
        self.connection = sqlite3.connect(uri)

    def create_classes(self) -> None:
        CLASSES = 'CREATE TABLE IF NOT EXISTS Classes (' \
                  'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                  'name TEXT UNIQUE NOT NULL,' \
                  'dnevnik_id INTEGER UNIQUE NOT NULL);'
        cursor = self.connection.cursor()
        cursor.execute(CLASSES)
        cursor.close()

    def create_timetable(self) -> None:
        TIMETABLE = 'CREATE TABLE IF NOT EXISTS Timetable (' \
                    'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                    'date TEXT NOT NULL,' \
                    'lesson_number INTEGER NOT NULL,' \
                    'lesson_name TEXT NULL,' \
                    'lesson_room TEXT NULL,' \
                    'lesson_teacher TEXT NULL,' \
                    'lesson_time TEXT NULL,' \
                    'classes_id INTEGER,' \
                    'FOREIGN KEY (classes_id) REFERENCES Classes (id));'
        cursor = self.connection.cursor()
        cursor.execute(TIMETABLE)
        cursor.close()

    def delete_all(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS Classes;')
        cursor.execute('DROP TABLE IF EXISTS Timetable;')
        cursor.close()

    def add_new_class(self,
                      name: str,
                      dnevnik_id: int) -> str:
        cursor = self.connection.cursor()
        CLASSES = 'SELECT id' \
                  'FROM Classes' \
                  f'WHERE name = {name}' \
                  f'AND dnevnik_id = {dnevnik_id};'
        dbquery = cursor.execute(CLASSES)

        if dbquery is None:
            NEWCLASSES = 'INSERT INTO Classes (' \
                         'name,' \
                         'dnevnik_ru)' \
                         f'VALUES ({name}, {dnevnik_id});'
            cursor.execute(NEWCLASSES)
            message = 'Added new Classes'
        else:
            message = 'Classes already added'
        cursor.close()
        return message

    def add_new_timetable(self,
                          name: str,
                          dnevnik_id: int,
                          date: str,
                          lesson_number: int,
                          lesson_name: str,
                          lesson_room: str,
                          lesson_teacher: str,
                          lesson_time: str) -> None:
        cursor = self.connection.cursor()
        LINKCLASSES = 'SELECT id' \
                      'FROM Classes' \
                      f'WHERE name = {name}' \
                      f'AND dnevnik_id = {dnevnik_id};'
        NEWTIMETABLE = "INSERT INTO Timetable (" \
                       "date," \
                       "lesson_number," \
                       "lesson_name," \
                       "lesson_room," \
                       "lesson_teacher," \
                       "lesson_time," \
                       "classes_id)" \
                       f"VALUES ({date}, {lesson_number}, {lesson_name}," \
                       f"{lesson_room}, {lesson_teacher}, {lesson_time}," \
                       f"{LINKCLASSES});"
        cursor.execute(NEWTIMETABLE)
        cursor.close()

    def update_timetable(self,
                         name: str,
                         dnevnik_id: int,
                         date: str,
                         lesson_number: int,
                         lesson_name: str = None,
                         lesson_room: str = None,
                         lesson_teacher: str = None,
                         lesson_time: str = None) -> None:
        cursor = self.connection.cursor()
        NEWTIMETABLE = 'UPDATE Timetable' \
                       f'SET date = {date},' \
                       f'lesson_number = {lesson_number},' \
                       f'lesson_name = {lesson_name},' \
                       f'lesson_room = {lesson_room},' \
                       f'lesson_teacher = {lesson_teacher},' \
                       f'lesson_time = {lesson_time}' \
                       'WHERE classes_id IN (SELECT id FROM Classes' \
                       f'WHERE name = {name}' \
                       f'AND dnevnik_id = {dnevnik_id});'
        cursor.execute(NEWTIMETABLE)
        cursor.close()

    def get_timetable_by_classes_and_date(self,
                                          name: str,
                                          date: str) -> list:
        cursor = self.connection.cursor()
        QUERY = 'SELECT *' \
                'FROM Timetable' \
                f'WHERE date = {date}' \
                'AND classes_id IN (SELECT id FROM Classes' \
                f'WHERE name = {name});'
        dbquery = cursor.execute(QUERY)
        result = dbquery.fetchall()
        cursor.close()
        return result
