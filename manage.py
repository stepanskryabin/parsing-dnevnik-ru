import sys
from time import process_time
import inspect
import configparser

import sqlobject as orm
import click

from models import db

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
logging = config['LOGGING']
DB = config["DATABASE"]
# ************** END **********************************


@click.command()
@click.option("--database",
              type=click.Choice(["create", "delete"]),
              help='Create or delete all table '
              'with all data. Оperation, '
              'by default, creates all tables')
def main(database):
    # Connect to database
    connection = orm.connectionForURI(DB.get("uri"))
    orm.sqlhub.processConnection = connection
    # looking for all Classes listed in models.py
    classes = [cls_name for cls_name, cls_obj
               in inspect.getmembers(sys.modules['models.db'])
               if inspect.isclass(cls_obj)]

    if database == "create":
        start_time = process_time()
        for item in classes:
            # Create tables in database for each class
            # that is located in models modules
            class_ = getattr(db, item)
            class_.createTable(ifNotExists=True)
        click.echo(f'Table is createt at: '
                   f'{process_time() - start_time} sec.')
    elif database == "delete":
        start_time = process_time()
        for item in classes:
            class_ = getattr(db, item)
            class_.dropTable(ifExists=True, dropJoinTables=True, cascade=True)
        click.echo(f'Table is deleted at: '
                   f'{process_time() - start_time} sec.')


if __name__ == "__main__":
    main()
