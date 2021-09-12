import configparser

from flask import Flask
from flask import render_template, url_for
import sqlobject as orm

# ************** Logging beginning *******************
from loguru import logger
from controller.logger import add_logging
# ************** Unicorn logger off ******************
import logging
logging.disable()
# ************** Logging end *************************

config = configparser.ConfigParser()
config.read("config.ini")
database = config['DATABASE']
LOG = config['LOGGING']

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
    return render_template("index.html", classes=classes)


@app.route('/schedules/<name>')
def schedules(name):
    return render_template("schedules.html", classname=name)
