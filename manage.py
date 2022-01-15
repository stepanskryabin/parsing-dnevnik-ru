from time import process_time

import click

from db.dbhandler import DBHandler
from controller.config import DB

db = DBHandler(DB.get('uri'))


@click.command()
@click.option("--database",
              type=click.Choice(["create", "delete"]),
              help='Create or delete all table '
              'with all data. Operation, '
              'by default, creates all tables')
def main(database,
         schedules):
    if database == "create":
        start_time = process_time()
        db.create()
        click.echo(f'Table is created at: '
                   f'{process_time() - start_time} sec.')
    elif database == "delete":
        start_time = process_time()
        db.delete()
        click.echo(f'Table is deleted at: '
                   f'{process_time() - start_time} sec.')


if __name__ == "__main__":
    main()
