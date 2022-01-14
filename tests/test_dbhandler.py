import unittest
from loguru import logger
from sqlite3 import OperationalError

from db.dbhandler import DBHandler


class TestDBHandlerMainMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.db = DBHandler(uri=":memory:")

    def setUp(self) -> None:
        self.db.create_classes()
        self.db.create_timetable()

    def test_create_table_in_database(self) -> None:
        self.db.add_classes(name='1А',
                            dnevnik_id=123)
        self.db.add_timetable(name='1А',
                              dnevnik_id=123,
                              date='2021-12-12',
                              lesson_number=1,
                              lesson_name='История',
                              lesson_room='216',
                              lesson_teacher='Иванов',
                              lesson_time='08:40-09:00')
        classes = self.db.get_classes(name='1А',
                                      dnevnik_id=123)
        timetable = self.db.get_timetable(name='1А',
                                          dnevnik_id=123,
                                          date='2021-12-12',
                                          lesson_number=1)
        self.assertIsInstance(classes, tuple)
        self.assertIsInstance(timetable, tuple)
        self.assertTupleEqual(classes[0], (1, '1А', 123))
        self.assertTupleEqual(timetable[0], (1, '2021-12-12', 1,
                                             'История', '216', 'Иванов',
                                             '08:40-09:00', 1))

    def test_delete_database(self) -> None:
        self.db.delete_all()
        self.assertRaises(OperationalError,
                          self.db.get_classes,
                          name="1А",
                          dnevnik_id=123)

    def test_str(self) -> None:
        self.assertEqual(str(self.db),
                         "Connected to database in :memory:")

    def test_repr(self) -> None:
        self.assertEqual(repr(self.db),
                         "class DBHandler: paramstyle=named")


class TestDBHandlerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logger.remove()
        cls.db = DBHandler(uri=":memory:")

    def setUp(self) -> None:
        self.db.create_classes()
        self.db.create_timetable()
        self.db.add_classes(name="1А",
                            dnevnik_id=1)
        self.db.add_classes(name="2А",
                            dnevnik_id=2)
        self.db.add_timetable(name="1А",
                              dnevnik_id=1,
                              date="2021-11-01",
                              lesson_number=2,
                              lesson_name="Программирование",
                              lesson_room="216",
                              lesson_teacher="Гвидо ван Россум",
                              lesson_time="с 10:00 до 13:00")
        self.db.add_timetable(name="2А",
                              dnevnik_id=2,
                              date="2021-11-01",
                              lesson_number=1,
                              lesson_name="Программирование",
                              lesson_room="216",
                              lesson_teacher="Гвидо ван Россум",
                              lesson_time="с 08:00 до 09:40")

    def tearDown(self) -> None:
        self.db.delete_all()

    def test_get_classes(self) -> None:
        dbquery = self.db.get_classes(name='1А',
                                      dnevnik_id=1)
        self.assertIsInstance(dbquery, tuple)
        self.assertEqual(dbquery[0], (1, '1А', 1))

    def test_add_classes(self) -> None:
        dbquery = self.db.add_classes(name="3А",
                                      dnevnik_id=3)
        self.assertEqual(dbquery, 'Ok')

    def test_get_timetable(self) -> None:
        dbquery = self.db.get_timetable(name='2А',
                                        dnevnik_id=2,
                                        date="2021-11-01",
                                        lesson_number=1)
        self.assertIsInstance(dbquery, tuple)
        self.assertTupleEqual(dbquery[0], (2, "2021-11-01", 1,
                                           "Программирование",
                                           "216", "Гвидо ван Россум",
                                           "с 08:00 до 09:40", 2))

    def test_add_timetable(self) -> None:
        dbquery = self.db.add_timetable(name="3А",
                                        dnevnik_id=3,
                                        date="2021-12-12",
                                        lesson_number=3,
                                        lesson_name="Физика",
                                        lesson_room="220",
                                        lesson_teacher="Иванов Иван",
                                        lesson_time="11:00-11:40")
        self.assertEqual(dbquery, "Ok")

    def test_get_timetable_by_classes_and_date(self) -> None:
        dbquery = self.db.get_timetable_by_classes_and_date(name="1А",
                                                            date="2021-11-01")
        self.assertEqual(dbquery[0].lesson_number, 2)
