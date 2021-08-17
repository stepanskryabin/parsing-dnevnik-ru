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

config = configparser.ConfigParser()
config.read("config.ini")
database = config['DATABASE']

# loguru logger on
add_logging(logging.getint("level"))


# Подключаемся к БД
try:
    connection = orm.connectionForURI(database.get("uri"))
except Exception as ERROR:
    logger.exception(str(ERROR))
finally:
    orm.sqlhub.processConnection = connection


app = Flask(__name__)


@app.route('/')
def start_page():
    return render_template("index.html")
