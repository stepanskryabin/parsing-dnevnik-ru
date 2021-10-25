import configparser
from datetime import date

from flask import Flask
from flask import render_template
import sqlobject as orm
from sqlobject import AND

from controller import convtime
from models import db

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
database = config['DATABASE']
LOG = config['LOGGING']
PARAMETERS = config["PARAMETERS"]
# ****************************************************

# loguru logger on
add_logging(LOG.getint("level"))


# Подключаемся к БД
try:
    connection = orm.connectionForURI(database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = connection


app = Flask(__name__)
TODAY = date.today()


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
    classes_dbquery = db.Classes.selectBy(name=name).getOne()
    for item in WEEK_LIST:
        dbquery = db.Timetable.select(AND(db.Timetable.q.date == str(item),
                                      db.Timetable.q.classes == classes_dbquery.id))
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
