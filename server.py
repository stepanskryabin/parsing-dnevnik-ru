from datetime import date

from flask import Flask
from flask import render_template

from controller import convtime
<<<<<<< HEAD
from db import dbhandler
from controller.config import LOGGING
from controller.config import DB
=======
from models import dbhandler
>>>>>>> main

# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging


logging.disable()
# ************** Logging end *************************

<<<<<<< HEAD

# loguru logger on
add_logging(LOGGING.getint("level"))
=======
# ****************************************************
config = configparser.ConfigParser()
config.read("config.ini")
DB = config['DATABASE']
LOG = config['LOGGING']
PARAMETERS = config["PARAMETERS"]
# ****************************************************

# loguru logger on
add_logging(LOG.getint("level"))

# Подключаемся к БД
db = dbhandler.DBHandler(DB.get("uri"))
>>>>>>> main

app = Flask(__name__)

TODAY = date.today()
<<<<<<< HEAD
# TODAY = date.fromisoformat("2021-11-12")
=======
#TODAY = date(2021, 10, 1)
>>>>>>> main


@app.route("/")
@app.route('/home')
def home():
    classes = ("1а", "1б", "1в",
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
    years = f"{TODAY.year-1} / {TODAY.year}"
    return render_template("index.html",
                           classes=classes,
                           years=years)


@app.route('/schedules/<name>-<int:page_id>')
def schedules(name, page_id):
    month = {
        "1": "января",
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
        "12": "декабря"
        }
    db = dbhandler.DBHandler(DB.get("uri"))
    WEEK_LIST = convtime.date_on_week(TODAY, page_id)
    logger.debug(f"Список дат дней недели{WEEK_LIST}")
    query_list = []
<<<<<<< HEAD
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

=======
    row_list = []
    for item in WEEK_LIST:
        dbquery = db.get_timetable_by_classes(name=name,
                                              date=str(item))
        logger.debug(f"DBQUERY: {list(dbquery)}")
        for element in dbquery:
            row = element.lesson_number
            row_list.append(row)
        query_list.append(dbquery)
    query_list = tuple(query_list)
    row_list = set(row_list)
    logger.debug(f"ROW_LIST: {row_list}")
    col_name = ("Урок", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС")
    week = ({"start": str(WEEK_LIST[0]),
             "end": str(WEEK_LIST[6])},
            {"start": str(WEEK_LIST[0]),
             "end": str(WEEK_LIST[6])})
>>>>>>> main
    return render_template("schedules.html",
                           classname=name,
                           timetables=query_list,
                           row_lesson=set(row_lesson),
                           page_id=page_id,
                           start_month=month[f"{WEEK_LIST[0].date.month}"],
                           start_date=WEEK_LIST[0].date.day,
                           stop_month=month[f"{WEEK_LIST[6].date.month}"],
                           stop_date=WEEK_LIST[6].date.day,
                           week_list=str_date)


if __name__ == "__main__":
    app.run()
