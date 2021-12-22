import inspect
import sys

import sqlobject as orm
from sqlobject.main import SQLObjectIntegrityError
from sqlobject.main import SQLObjectNotFound
from sqlobject.sresults import SelectResults
from sqlobject.main import SQLObject
from sqlobject import AND

from db import models

import sqlite3

class DatabaseReadError(SQLObjectNotFound):
    pass


class DatabaseAccessError(Exception):
    pass


class DatabaseWriteError(SQLObjectNotFound):
    pass


class DBHandler:
    def __init__(self,
                 uri: str = "sqlite:/:memory:",
                 debug: bool = False,
                 logger: str = None,
                 loglevel: str = None,
                 path_to_models: str = "db.models") -> None:

        if debug and logger and loglevel:
            self._debug = "1"
            self._logger = logger
            self._loglevel = loglevel
            self._uri = "".join((uri,
                                 f"?debug={self._debug}",
                                 f"?logger={self._logger}",
                                 f"?loglevel={self._loglevel}"))
        else:
            self._uri = uri
            self._debug = "0"
            self._logger = None
            self._loglevel = None

        self.connection = sqlite3.connect(database=uri)
        self._cursor = self.connection.cursor()
        self.path = path_to_models

    def __str__(self) -> str:
        return f"Connected to database: {self._uri}"

    def __repr__(self) -> str:
        return "".join((f"class {self.__class__.__name__}: ",
                        f"debug={self._debug} ",
                        f"logger={self._logger} ",
                        f"loglevel={self._loglevel}"))

    def __search_db_in_models(self) -> tuple:
        classes = [cls_name for cls_name, cls_obj
                   in inspect.getmembers(sys.modules[self.path])
                   if inspect.isclass(cls_obj)]
        return tuple(classes)

    def create(self) -> None:
        self._cursor.execute('''CREATE TABLE Classes (
                                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    name TEXT UNIQUE,
                                    dnevnik_id INTEGER UNIQUE,
                                    timetable 
                                    )''')
        return

    def delete(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True,
                             dropJoinTables=True,
                             cascade=True,
                             connection=self.connection)
        return

    @property
    def debug(self) -> bool | None:
        if self._debug == "0":
            return False
        else:
            return True

    @debug.setter
    def debug(self,
              value: bool = False) -> None:
        if value is True:
            self._debug = "1"
        self._uri = "".join((self._uri,
                             f"?debug={self._debug}"))
        self.connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self.connection

    def __read_db(self,
                  table: str,
                  get_one: bool,
                  **kwargs) -> SelectResults | SQLObject:
        # The SelectResults object type when the result
        # is in the form of a list. SQLObject type when
        # the result is a single object.
        db = getattr(models, table)
        if get_one:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs).getOne()
            except (SQLObjectNotFound, SQLObjectIntegrityError):
                raise DatabaseReadError
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery
        else:
            try:
                dbquery = db.selectBy(self.connection,
                                      **kwargs)
            except SQLObjectNotFound:
                raise DatabaseReadError
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery

    @staticmethod
    def __write_db(table: str,
                   **kwargs) -> SQLObject:
        db = getattr(models, table)
        try:
            dbquery = db(**kwargs)
        except (Exception, SQLObjectIntegrityError) as err:
            raise DatabaseWriteError from err
        else:
            return dbquery

    def get_all_classes(self) -> SelectResults:
        return self.__read_db(table="Classes",
                              get_one=False)

    def get_classes_by_name_and_id(self,
                                   name: str,
                                   dnevnik_id: int) -> SelectResults:
        return self.__read_db(table="Classes",
                              get_one=True,
                              name=name,
                              dnevnik_id=dnevnik_id)

    def add_new_class(self,
                      name: str,
                      dnevnik_id: int) -> SQLObject:
        return self.__write_db(table="Classes",
                               name=name,
                               dnevnik_id=dnevnik_id)

    def add_new_timetable(self,
                          name: str,
                          dnevnik_id: int,
                          date: str,
                          lesson_number: int,
                          lesson_name: str,
                          lesson_room: str,
                          lesson_teacher: str,
                          lesson_time: str) -> SQLObject:
        try:
            dbquery = self.get_classes_by_name_and_id(name=name,
                                                      dnevnik_id=dnevnik_id)
        except DatabaseReadError:
            dbquery = self.add_new_class(name=name,
                                         dnevnik_id=dnevnik_id)
        finally:
            return self.__write_db(table="Timetable",
                                   date=date,
                                   lesson_number=lesson_number,
                                   lesson_name=lesson_name,
                                   lesson_room=lesson_room,
                                   lesson_teacher=lesson_teacher,
                                   lesson_time=lesson_time,
                                   classes=dbquery.id)

    def update_timetable(self,
                         name: str,
                         dnevnik_id: int,
                         date: str,
                         lesson_number: int,
                         lesson_name: str = None,
                         lesson_room: str = None,
                         lesson_teacher: str = None,
                         lesson_time: str = None) -> bool:

        try:
            db_class = self.__read_db(table="Classes",
                                      get_one=True,
                                      name=name,
                                      dnevnik_id=dnevnik_id)
            dbquery = self.__read_db(table="Timetable",
                                     get_one=True,
                                     date=date,
                                     lesson_number=lesson_number,
                                     classes=db_class.id)
        except (DatabaseReadError, DatabaseAccessError):
            return False
        else:
            dbquery.lesson_name = lesson_name
            dbquery.lesson_room = lesson_room
            dbquery.lesson_teacher = lesson_teacher
            dbquery.lesson_time = lesson_time
            return True

    def get_timetable_by_classes_and_date(self,
                                          name: str,
                                          date: str) -> SelectResults:
        classes = self.__read_db(table="Classes",
                                 get_one=True,
                                 name=name)
        return models.Timetable.select(AND(
                                       models.Timetable.q.date == date,
                                       models.Timetable.q.classes == classes))
