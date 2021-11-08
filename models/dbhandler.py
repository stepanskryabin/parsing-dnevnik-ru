import configparser
import inspect
import sys

import sqlobject as orm
from sqlobject.main import SQLObjectIntegrityError, SQLObjectNotFound
from sqlobject.main import SelectResults
from sqlobject.sqlbuilder import AND

from models import models
from controller.config import DB


class DatabaseReadError(SQLObjectNotFound):
    pass


class DatabaseAccessError(Exception):
    pass


class DatabaseWriteError(SQLObjectNotFound):
    pass


class DBHandler:
    def __init__(self,
                 uri: str = DB.get("uri")) -> None:
        self._uri = uri
        self._connection = orm.connectionForURI(self._uri)
        orm.sqlhub.processConnection = self._connection

    def __str__(self):
        return f"Connect to database: {self._uri}"

    def __repr__(self):
        return f"{self.__class__.__name__} at uri: {self._uri}"

    @staticmethod
    def __search_db_in_models(path: str = 'models.models') -> tuple:
        classes = [cls_name for cls_name, cls_obj
                   in inspect.getmembers(sys.modules[path])
                   if inspect.isclass(cls_obj)]
        return tuple(classes)

    def create(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            # Create tables in database for each class
            # that is located in models module
            class_ = getattr(models, item)
            class_.createTable(ifNotExists=True,
                               connection=self._connection)
        return "Ok"

    def delete(self) -> None:
        # looking for all Classes listed in models.py
        for item in self.__search_db_in_models():
            class_ = getattr(models, item)
            class_.dropTable(ifExists=True, 
                             dropJoinTables=True,
                             cascade=True,
                             connection=self._connection)
        return "Ok"

    def __read_classes(self,
                       get_one: bool,
                       **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.Classes.selectBy(self._connection,
                                                  **kwargs).getOne()
            except SQLObjectNotFound:
                raise DatabaseReadError("Class is not in the database")
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery
        else:
            try:
                dbquery = models.Classes.selectBy(self._connection,
                                                  **kwargs)
            except SQLObjectNotFound:
                raise DatabaseReadError("No classes data in the database")
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery

    def __write_classes(self,
                        **kwargs) -> models.Classes:
        try:
            dbquery = models.Classes(**kwargs)
        except SQLObjectIntegrityError:
            raise DatabaseWriteError("Writing is restricted")
        except Exception as err:
            raise DatabaseAccessError from err
        else:
            return dbquery

    def __read_timetables(self,
                          get_one: bool,
                          **kwargs) -> SelectResults:
        if get_one:
            try:
                dbquery = models.Timetable.selectBy(self._connection,
                                                    **kwargs).getOne()
            except SQLObjectNotFound:
                raise DatabaseReadError("Timetable is not in the database")
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery
        else:
            try:
                dbquery = models.Timetable.selectBy(self._connection,
                                                    **kwargs)
            except SQLObjectNotFound:
                raise DatabaseReadError("No timetables data in the database")
            except Exception as err:
                raise DatabaseAccessError from err
            else:
                return dbquery

    def __write_timetables(self,
                           **kwargs) -> models.Timetable:
        try:
            dbquery = models.Timetable(**kwargs)
        except SQLObjectIntegrityError:
            raise DatabaseWriteError("Writing is restricted")
        except Exception as err:
            raise DatabaseAccessError from err
        else:
            return dbquery

    def get_classes_by_name_and_id(self,
                                   name: str,
                                   dnevnik_id: int) -> SelectResults:
        return self.__read_classes(get_one=True,
                                   name=name,
                                   dnevnik_id=dnevnik_id)

    def add_new_class(self,
                      name: str,
                      dnevnik_id: int) -> None:
        return self.__write_classes(name=name,
                                    dnevnik_id=dnevnik_id)

    def add_new_timetable(self,
                          name: str,
                          dnevnik_id: int,
                          date: str,
                          lesson_number: int,
                          lesson_name: str,
                          lesson_room: str,
                          lesson_teacher: str,
                          lesson_time: str) -> None:
        try:
            dbquery = self.get_classes_by_name_and_id(name=name,
                                                      dnevnik_id=dnevnik_id)
        except DatabaseReadError:
            new_class = self.add_new_class(name=name,
                                           dnevnik_id=dnevnik_id)
        else:
            new_class = dbquery.id
        finally:
            return self.__write_timetables(date=date,
                                           lesson_number=lesson_number,
                                           lesson_name=lesson_name,
                                           lesson_room=lesson_room,
                                           lesson_teacher=lesson_teacher,
                                           lesson_time=lesson_time,
                                           classes=new_class)

    def get_timetable_by_classes(self,
                                 name: str,
                                 date: str) -> SelectResults:
        classes = self.__read_classes(get_one=True,
                                      name=name)
        return models.Timetable.select(AND(
                                       models.Timetable.q.date == date,
                                       models.Timetable.q.classes == classes))
