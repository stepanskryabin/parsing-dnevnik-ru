import os
import unittest

from loguru import logger

from parser import write_db
from parser import get_lessons
from parser import get_classes
from parser import get_schedules

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
CLASSES = os.path.join(FIXTURES_PATH, "classes.html")
SCHEDULES = os.path.join(FIXTURES_PATH, "schedules.html")


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        logger.remove()
        with open(SCHEDULES, 'r') as f:
            self.test_lessons = f.read()
        with open(CLASSES, 'r') as f:
            self.test_classes = f.read()
        self.test_schedules = get_classes(self.test_classes)

    def tearDown(self) -> None:
        del self.test_lessons
        del self.test_classes

    def test_get_lessons(self):
        result = get_lessons(self.test_lessons)
        self.assertEqual(result[0].classes_name, "2а")

    def test_write_db(self):
        lessons = get_lessons(self.test_lessons)
        result = write_db(lessons[0])
        self.assertEqual(result, 'Ok')

    def test_get_classes(self):
        result = get_classes(self.test_classes)
        self.assertEqual(result[0].class_id, '1849711203825070779')

    def test_get_schedules(self):
        classes = get_classes(self.test_classes)
        links = get_schedules(classes,
                              start_year=2022,
                              start_month=1,
                              start_day=15,
                              deep_day=7)
        for link in links:
            self.assertEqual(link.split(sep='dnevnik.ru')[0],
                             'https://schools.')
