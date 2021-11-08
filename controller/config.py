import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8-sig")

USER = config['USER']
PARAMETERS = config['PARAMETERS']
OTHER = config['OTHER']
LOGGING = config['LOGGING']
DNEVNIK_RU = config['DNEVNIK_RU']
TRIMESTER = config['TRIMESTER']
DB = config["DATABASE"]
SCHEDULES = config["SCHEDULES"]
