from os import name as OS_NAME

from crontab import CronTab


class Schedule:
    def __init__(self,
                 period: int,
                 tabfile: str = None) -> None:
        self._job = CronTab(user=True)
        self.period = period
        self._comment = "update_db"
        self._path = "/code/parsing-dnevnik-ru/"
        self._tabfile = tabfile

        if OS_NAME == 'posix':
            self._cron = CronTab(user=True)
            self._command = "".join((f"cd $HOME{self._path} && "
                                         "pipenv run python ",
                                         f"$HOME{self._path}parser.py"))
        elif OS_NAME == 'nt':
            if self._tabfile is None:
                self._tabfile = 'win_cron.tab'
            self._cron = CronTab(tabfile=self._tabfile)
            self._command = "".join(("python ",
                                     "$PARSER/parser.py"))

    def delete(self) -> str:
        self._cron.remove_all(comment=self._comment)
        return "All job's delete"

    def create(self) -> str:
        self._job = self._cron.new(command=self._command,
                                   comment=self._comment)
        self._job.hour.every(self.period)
        if OS_NAME == "posix":
            self._cron.write_to_user(user=True)
        elif OS_NAME == "nt":
            self._cron.write(self._tabfile)
        return "Job created"

    def run(self) -> str:
        self._job.run()
        return "Job is running"
