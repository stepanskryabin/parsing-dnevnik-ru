import configparser

from flask import Flask
from flask import render_template
import sqlobject as orm

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


@app.route("/")
@app.route('/home')
def home():
    classes = ("1А", "1Б", "1В",
               "2А", "2Б", "2В", "2Г", "2Д",
               "3А", "3Б", "3В", "3Г",
               "4А", "4Б", "4В",
               "5А", "5Б", "5В",
               "6А", "6Б", "6В",
               "7А", "7Б", "7В",
               "8А", "8Б", "8В",
               "9А", "9Б", "9В",
               "10",
               "11")
    years = f"{PARAMETERS.getint('year')} / {PARAMETERS.getint('year') + 1}"
    return render_template("index.html",
                           classes=classes,
                           years=years)


@app.route('/schedules/<name>-<int:page_id>')
def schedules(name, page_id):
    col_name = ("Урок", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС")
    row_name = (str(x) for x in range(1, 13))
    lesson_name = ("Русский язык", "Математика", "ОБЖ", "История",
                   "Английский язык", "Физкультура", "Черчение")
    week = ({"start": "01 сентября",
             "end": "08 сентября"},
             {"start": "09 сентября",
             "end": "16 сентября"})
    return render_template("schedules.html",
                           classname=name,
                           columns=col_name,
                           rows=row_name,
                           lessons=lesson_name,
                           page_id=page_id,
                           week=week)
