from os import name as OS_NAME
from os import path

from crontab import CronTab


class Schedule:
    def __init__(self,
                 period: int,
                 tabfile: str = None) -> None:
        self._job = CronTab(user=True)
        self.period = period
        self._comment = "update_db"
        self._path = "/code/parsing-dnevnik-ru/"
        self.tabfile = tabfile
        self._path = path.abspath("")

        if OS_NAME == 'posix1':
            self._cron = CronTab(user=True)
            self._command = "".join((f"cd $HOME{self._path} && "
                                         "pipenv run python ",
                                         f"$HOME{self._path}parser.py"))
        elif OS_NAME == 'posix':
            if self.tabfile is None:
                self.tabfile = 'win_cron.tab'

            file_exists = path.exists(self.tabfile)
            if file_exists:
                self.tabfile = path.join(self._path,
                                          self.tabfile)
            else:
                filename = "".join((self._path,
                                    "/",
                                    self.tabfile))
                with open(filename, "w") as f:
                    f.write("")
                    f.close()

            self._cron = CronTab(tabfile=self.tabfile)
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
            self._cron.write(self.tabfile)
        return "Job created"

    def run(self) -> str:
        self._job.run()
        return "Job is running"
