import unittest
from datetime import date

from controller.convtime import filtred_by_week
from controller.convtime import date_on_week


class TestConvtime(unittest.TestCase):
    def setUp(self) -> None:
        self.test_date = (date(2021, 12, 12), date(2021, 12, 13))

    def tearDown(self) -> None:
        del self.test_date

    def test_filtred_by_week(self) -> None:
        result = filtred_by_week(year=2021,
                                 month=12,
                                 day=12,
                                 deep_day=7)
        self.assertIsInstance(result, set)
        self.assertSetEqual(result, set(self.test_date))

    def test_date_on_week(self) -> None:
        result = date_on_week(today=self.test_date[0],
                              week=1)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0].name, "ПН")
        self.assertEqual(result[0].date, date(2021, 12, 6))
        self.assertEqual(result[0].str_date, "2021-12-06")
