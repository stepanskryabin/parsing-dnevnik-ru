from datetime import date

from flask import Flask
from flask import render_template

from controller import convtime
from db import dbhandler
from controller.config import LOGGING
from controller.config import DB

# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging


logging.disable()
# ************** Logging end *************************


# loguru logger on
add_logging(LOGGING.getint("level"))

app = Flask(__name__)

TODAY = date.today()
# TODAY = date.fromisoformat("2021-11-12")

CLASSES = ("1а", "1б", "1в",
           "2а", "2б", "2в", "2г", "2д",
           "3а", "3б", "3в", "3г",
           "4а", "4б", "4в",
           "5а", "5б", "5в",
           "6а", "6б", "6в",
           "7а", "7б", "7в",
           "8а", "8б", "8в",
           "9а", "9б", "9в",
           "10",
           "11")

MONTH = {"1": "января",
         "2": "февраля",
         "3": "марта",
         "4": "апреля",
         "5": "мая",
         "6": "июня",
         "7": "июля",
         "8": "августа",
         "9": "сентября",
         "10": "октября",
         "11": "ноября",
         "12": "декабря"}


@app.route("/")
@app.route('/home')
def home() -> str:
    return render_template("index.html",
                           classes=CLASSES,
                           years=f"{TODAY.year-1} / {TODAY.year}")


@app.route('/schedules/<name>-<int:page_id>')
def schedules(name: str,
              page_id: int) -> str:
    db = dbhandler.DBHandler(DB.get("uri"))

    WEEK_LIST = convtime.date_on_week(TODAY, page_id)
    logger.debug(f"Список дат дней недели{WEEK_LIST}")

    query_list = []
    row_lesson = []

    for week in WEEK_LIST:
        dbquery = db.get_timetable_by_classes_and_date(name=name,
                                                       date=week.str_date)
        for item in dbquery:
            query_list.append(item)
            if item.lesson_name != "" and item.lesson_room != "":
                row_lesson.append(item.lesson_number)

    logger.debug(f"Timetable: {list(query_list)}")
    logger.debug(f"ROW: {set(row_lesson)}")

    str_date = []
    for week in WEEK_LIST:
        str_date.append(week.str_date)

    return render_template("schedules.html",
                           classname=name,
                           timetables=query_list,
                           row_lesson=set(row_lesson),
                           page_id=page_id,
                           start_month=MONTH[f"{WEEK_LIST[0].date.month}"],
                           start_date=WEEK_LIST[0].date.day,
                           stop_month=MONTH[f"{WEEK_LIST[6].date.month}"],
                           stop_date=WEEK_LIST[6].date.day,
                           week_list=str_date)


if __name__ == "__main__":
    app.run()
