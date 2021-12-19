import unittest
from loguru import logger

from sqlobject.main import SQLObject
from sqlobject.sresults import SelectResults

from db.dbhandler import DBHandler
from db import models
from db.dbhandler import DatabaseAccessError
from db.dbhandler import DatabaseWriteError
from db.dbhandler import DatabaseReadError


class TestDBHandlerMainMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()

    def tearDown(self):
        self.db.delete()

    def test_create_database(self):
        dbquery = self.db.get_all_classes()
        self.assertIsInstance(dbquery, SelectResults)

    def test_delete_database(self):
        self.db.delete()
        self.assertRaises(DatabaseAccessError,
                          self.db.get_classes_by_name_and_id,
                          name="2В",
                          dnevnik_id=123)

    def test_search_db_in_models(self):
        self.db.delete()
        dbquery = self.db._DBHandler__search_db_in_models()
        self.assertIsInstance(dbquery, tuple)
        self.assertEqual(dbquery[0], 'Classes')

    def test_create_db_not_set_debug(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:")
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True)
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug_logger(self):
        self.db.delete()
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True,
                       logger='Test')
        self.assertFalse(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:")

    def test_create_db_set_debug_logger_loglevel(self):
        db = DBHandler(uri="sqlite:/:memory:",
                       debug=True,
                       logger='Test',
                       loglevel='debug')
        self.assertTrue(db.debug)
        self.assertEqual(db._uri,
                         "sqlite:/:memory:?debug=1?logger=Test?loglevel=debug")

    def test_str(self):
        self.assertEqual(str(self.db),
                         "Connected to database: sqlite:/:memory:")

    def test_repr(self):
        self.assertEqual(repr(self.db),
                         "class DBHandler: debug=0 logger=None loglevel=None")


class TestDBHandlerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.remove()
        cls.db = DBHandler(uri="sqlite:/:memory:")

    def setUp(self):
        self.db.create()
        self.db.add_new_class(name="1А",
                              dnevnik_id=1)
        self.db.add_new_class(name="2А",
                              dnevnik_id=2)
        self.db.add_new_timetable(name="1А",
                                  dnevnik_id=1,
                                  date="2021-11-01",
                                  lesson_number=2,
                                  lesson_name="Программирование",
                                  lesson_room="216",
                                  lesson_teacher="Гвидо ван Россум",
                                  lesson_time="с 10:00 до 13:00")
        self.db.add_new_timetable(name="2А",
                                  dnevnik_id=2,
                                  date="2021-11-01",
                                  lesson_number=1,
                                  lesson_name="Программирование",
                                  lesson_room="216",
                                  lesson_teacher="Гвидо ван Россум",
                                  lesson_time="с 08:00 до 09:40")

    def tearDown(self):
        self.db.delete()

    def test_read_db(self):
        dbquery_one = self.db._DBHandler__read_db(table="Classes",
                                                  get_one=True,
                                                  name="1А")
        dbquery_many = self.db._DBHandler__read_db(table="Classes",
                                                   get_one=False)
        self.assertEqual(dbquery_one.dnevnik_id, 1)
        self.assertEqual(dbquery_many.count(), 2)
        self.assertIsInstance(dbquery_many,
                              SelectResults)
        self.assertRaises(DatabaseReadError,
                          self.db._DBHandler__read_db,
                          table="Classes",
                          get_one=True,
                          name="1В")
        self.db.delete()
        self.assertRaises(DatabaseAccessError,
                          self.db._DBHandler__read_db,
                          table="Classes",
                          get_one=True,
                          uuid="1А")

    def test_write_db(self):
        dbquery = self.db._DBHandler__write_db(table="Classes",
                                               name="11",
                                               dnevnik_id=3)
        self.assertIsInstance(dbquery, models.Classes)
        self.assertRaises(DatabaseWriteError,
                          self.db._DBHandler__write_db,
                          table="Timetable",
                          date="2021-11-11",
                          lessom_number="6",
                          lesson_name="История",
                          lesson_room="305",
                          lesson_teacher="Петров Петр Петрович",
                          lesson_time="8:40-9:40")

    def test_get_debug(self):
        self.assertFalse(self.db.debug)

    def test_set_debug(self):
        self.db.debug = True
        self.assertTrue(self.db.debug)

    def test_get_all_classes(self):
        dbquery = self.db.get_all_classes()
        self.assertIsInstance(dbquery,
                              SelectResults)
        self.assertEqual(dbquery[0].name, "1А")

    def test_get_classes_by_name_and_id(self):
        dbquery = self.db.get_classes_by_name_and_id(name="2А",
                                                     dnevnik_id=2)
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.name, "2А")

    def test_add_new_class(self):
        dbquery = self.db.add_new_class(name="3А",
                                        dnevnik_id=3)
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.name, "3А")

    def test_add_new_timetable(self):
        dbquery = self.db.add_new_timetable(name="2А",
                                            dnevnik_id=2,
                                            date="2021-12-12",
                                            lesson_number=3,
                                            lesson_name="Физика",
                                            lesson_room="220",
                                            lesson_teacher="Иванов Иван",
                                            lesson_time="11:00-11:40")
        self.assertIsInstance(dbquery,
                              SQLObject)
        self.assertEqual(dbquery.lesson_name, "Физика")

    def test_update_timetable(self):
        db_update = self.db.update_timetable(name="2А",
                                             dnevnik_id=2,
                                             date="2021-11-01",
                                             lesson_number=1,
                                             lesson_name="Танцы",
                                             lesson_room="215",
                                             lesson_teacher="Гвидо ван Россум",
                                             lesson_time="с 08:00 до 09:40")
        self.assertTrue(db_update)
        dbquery = self.db.get_timetable_by_classes_and_date(name="2А",
                                                            date="2021-11-01")
        self.assertNotEqual(dbquery[0].lesson_room, "216")
        self.assertEqual(dbquery[0].lesson_name, "Танцы")

    def test_wrong_update_timetable(self):
        db_update = self.db.update_timetable(name="5А",
                                             dnevnik_id=10,
                                             date="2021-11-01",
                                             lesson_number=1,
                                             lesson_name="Танцы",
                                             lesson_room="215",
                                             lesson_teacher="Гвидо ван Россум",
                                             lesson_time="с 08:00 до 09:40")
        self.assertFalse(db_update)

    def test_get_timetable_by_classes(self):
        dbquery = self.db.get_timetable_by_classes_and_date(name="1А",
                                                            date="2021-11-01")
        self.assertEqual(dbquery[0].lesson_number, 2)
