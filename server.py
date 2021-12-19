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

# Подключаемся к БД
db = dbhandler.DBHandler(DB.get("uri"))

app = Flask(__name__)

TODAY = date.today()
# TODAY = date(2021, 10, 1)


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
    years = f"{TODAY.year} / {TODAY.year + 1}"
    return render_template("index.html",
                           classes=classes,
                           years=years)


@app.route('/schedules/<name>-<int:page_id>')
def schedules(name, page_id):

    WEEK_LIST = convtime.date_on_week(TODAY, page_id)
    logger.debug(f"Список дат дней недели{WEEK_LIST}")
    query_list = []

    for week in WEEK_LIST:
        dbquery = db.get_timetable_by_classes(name=name,
                                              date=week.str_date)
        for item in dbquery:
            query_list.append(item)

    logger.debug(f"Timetable: {list(query_list)}")

    str_date = []
    for week in WEEK_LIST:
        str_date.append(week.str_date)

    return render_template("schedules.html",
                           classname=name,
                           timetables=query_list,
                           page_id=page_id,
                           start_date=WEEK_LIST[0].str_date,
                           stop_date=WEEK_LIST[6].str_date,
                           week_list=str_date)


if __name__ == "__main__":
    app.run()
