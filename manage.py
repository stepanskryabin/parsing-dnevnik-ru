from time import process_time
import configparser

import click

from models import dbhandler

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
logging = config['LOGGING']
DB = config["DATABASE"]
# ************** END **********************************

db = dbhandler.DBHandler(DB.get('uri'))

@click.command()
@click.option("--database",
              type=click.Choice(["create", "delete"]),
              help='Create or delete all table '
              'with all data. Оperation, '
              'by default, creates all tables')
def main(database):
    if database == "create":
        start_time = process_time()
        db.create()
        click.echo(f'Table is createt at: '
                   f'{process_time() - start_time} sec.')
    elif database == "delete":
        start_time = process_time()
        db.delete()
        click.echo(f'Table is deleted at: '
                   f'{process_time() - start_time} sec.')


if __name__ == "__main__":
    main()
