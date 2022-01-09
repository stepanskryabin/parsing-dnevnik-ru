import sqlite3
from sqlite3 import DatabaseError
import copy
from collections import namedtuple


class DBHandler:
    def __init__(self,
                 uri: str = ":memory:") -> None:
        self.connection = sqlite3.connect(uri)
        self.cur = self.connection.cursor()
        sqlite3.paramstyle = "named"
        sqlite3.threadsafety = 3

    def __del__(self):
        self.connection.close()

    def create_classes(self) -> None:
        statement = '''CREATE TABLE IF NOT EXISTS Classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    dnevnik_id INTEGER UNIQUE NOT NULL);'''
        cursor = self.connection.cursor()
        cursor.execute(statement)
        self.connection.commit()
        cursor.close()

    def create_timetable(self) -> None:
        statement = '''CREATE TABLE IF NOT EXISTS Timetable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    lesson_number INTEGER NOT NULL,
                    lesson_name TEXT NULL,
                    lesson_room TEXT NULL,
                    lesson_teacher TEXT NULL,
                    lesson_time TEXT NULL,
                    classes_id INTEGER,
                    FOREIGN KEY (classes_id) REFERENCES Classes (id));'''
        cursor = self.connection.cursor()
        cursor.execute(statement)
        self.connection.commit()
        cursor.close()

    def delete_all(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS Classes;')
        cursor.execute('DROP TABLE IF EXISTS Timetable;')
        self.connection.commit()
        cursor.close()

    def get_classes(self,
                    name: str,
                    dnevnik_id: int) -> tuple:
        cursor = self.connection.cursor()
        statement = '''SELECT *
                    FROM Classes
                    WHERE name = :name
                    AND dnevnik_id = :dnevnik_id;'''
        dbquery = cursor.execute(statement, {"dnevnik_id": dnevnik_id,
                                             "name": name})
        return copy.deepcopy(dbquery.fetchone())

    def add_classes(self,
                    name: str,
                    dnevnik_id: int) -> str:
        cursor = self.connection.cursor()
        statement = '''INSERT INTO Classes (
                    name,
                    dnevnik_id)
                    VALUES (:name, :dnevnik_id);'''
        try:
            cursor.execute(statement, {"dnevnik_id": dnevnik_id,
                                       "name": name})
        except DatabaseError as err:
            return f'Error {str(err)}'
        else:
            self.connection.commit()
            cursor.close()
            return 'Ok'

    def get_timetable(self,
                      name: str,
                      dnevnik_id: int,
                      date: str,
                      lesson_number: int) -> tuple:
        cursor = self.connection.cursor()
        statement = '''SELECT *
                    FROM Timetable
                    WHERE date = :date
                    AND lesson_number = :lesson_number
                    AND classes_id IN (SELECT id FROM Classes
                                      WHERE name = :name
                                      AND dnevnik_id = :dnevnik_id);'''
        dbquery = cursor.execute(statement, {"name": name,
                                             "dnevnik_id": dnevnik_id,
                                             "date": date,
                                             "lesson_number": lesson_number})
        result = tuple(copy.deepcopy(dbquery.fetchall()))
        cursor.close()
        return result

    def add_timetable(self,
                      name: str,
                      dnevnik_id: int,
                      date: str,
                      lesson_number: int,
                      lesson_name: str,
                      lesson_room: str,
                      lesson_teacher: str,
                      lesson_time: str) -> str:
        cursor = self.connection.cursor()
        statement = '''INSERT INTO Timetable (
                    date,
                    lesson_number,
                    lesson_name,
                    lesson_room,
                    lesson_teacher,
                    lesson_time,
                    classes_id)
                    VALUES (:date, :lesson_number, :lesson_name,
                    :lesson_room, :lesson_teacher, :lesson_time,
                    (SELECT id FROM Classes
                    WHERE name = :name
                    AND dnevnik_id = :dnevnik_id));'''
        try:
            cursor.execute(statement, {"date": date,
                                       "lesson_number": lesson_number,
                                       "lesson_name": lesson_name,
                                       "lesson_room": lesson_room,
                                       "lesson_teacher": lesson_teacher,
                                       "lesson_time": lesson_time,
                                       "name": name,
                                       "dnevnik_id": dnevnik_id})
        except DatabaseError as err:
            return f'Error {str(err)}'
        else:
            self.connection.commit()
            cursor.close()
            return 'Ok'

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
        statement = '''UPDATE Timetable
                    SET date = :date,
                    lesson_number = :lesson_number,
                    lesson_name = :lesson_name,
                    lesson_room = :lesson_room,
                    lesson_teacher = :lesson_teacher,
                    lesson_time = :lesson_time
                    WHERE classes_id IN (SELECT id FROM Classes
                    WHERE name = :name
                    AND dnevnik_id = :dnevnik_id);'''
        cursor.execute(statement, {"date": date,
                                   "lesson_number": lesson_number,
                                   "lesson_name": lesson_name,
                                   "lesson_room": lesson_room,
                                   "lesson_teacher": lesson_teacher,
                                   "lesson_time": lesson_time,
                                   "name": name,
                                   "dnevnik_id": dnevnik_id})
        self.connection.commit()
        cursor.close()

    def get_timetable_by_classes_and_date(self,
                                          name: str,
                                          date: str) -> tuple:
        Timetable = namedtuple('Timetable', ["id",
                                             "date",
                                             "lesson_number",
                                             "lesson_name",
                                             "lesson_room",
                                             "lesson_teacher",
                                             "lesson_time"])
        result = []
        cursor = self.connection.cursor()
        statement = '''SELECT *
                    FROM Timetable
                    WHERE date = :date
                    AND classes_id IN (SELECT id FROM Classes
                    WHERE name = :name);'''
        dbquery = cursor.execute(statement, {"date": date,
                                             "name": name})
        all_row = tuple(copy.deepcopy(dbquery.fetchall()))
        for row in all_row:
            result.append(Timetable(id=row[0],
                                    date=row[1],
                                    lesson_number=row[2],
                                    lesson_name=row[3],
                                    lesson_room=row[4],
                                    lesson_teacher=row[5],
                                    lesson_time=row[6]))
        self.connection.commit()
        cursor.close()
        return tuple(result)
