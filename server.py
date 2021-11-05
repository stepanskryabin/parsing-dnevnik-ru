import configparser
from datetime import date

from flask import Flask
from flask import render_template

from controller import convtime
from models import dbhandler

# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging


logging.disable()
# ************** Logging end *************************

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

app = Flask(__name__)

TODAY = date.today()
#TODAY = date(2021, 10, 1)


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
    logger.debug(f"Список дат дней недели{str(WEEK_LIST)}")
    query_list = []
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
    return render_template("schedules.html",
                           classname=name,
                           columns=col_name,
                           rows=row_list,
                           timetables=query_list,
                           page_id=page_id,
                           week=week)

if __name__ == "__main__":
    app.run()
