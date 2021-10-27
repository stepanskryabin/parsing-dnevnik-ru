from crontab import CronTab
import configparser

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
SCHEDULES = config['SCHEDULES']
# ************** END **********************************

cron = CronTab(user=True)
cron.remove_all()
job = cron.new(command='cd /home/xamuh/code/parsing-dnevnik-ru/ && pipenv run python3 /home/xamuh/code/parsing-dnevnik-ru/parser.py',
               comment='update_db')
job.hour.every(SCHEDULES.getint('hour'))
cron.write()

job.run()
