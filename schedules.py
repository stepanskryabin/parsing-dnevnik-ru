from crontab import CronTab

cron = CronTab(user=True)
cron.remove_all()
job = cron.new(command='cd /home/xamuh/code/parsing-dnevnik-ru/ && pipenv run python3 /home/xamuh/code/parsing-dnevnik-ru/parser.py',
               comment='update_db')
job.hour.every(12)
cron.write()

job.run()
