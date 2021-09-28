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
