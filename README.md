# parsing-dnevik-ru

Утилита предназначена для парсинга расписаний с портала dnevnik.ru преобразования и вывода расписания (на текущую и следующую неделю) на экран терминала (киоска).

Для парсинга необходим логин и пароль к порталу.

## Установка

1. Установить Python версии 3.9 или выше.
2. Клонировать репозиторий git clone https://github.com/stepanskryabin/parsing-dnevnik-ru.git
3. Перейти в директорию parsing-dnevnik-ru
4. Настроить виртуальное окружение pipenv
5. Установить модули: Flask, selenium, beautifulsoup4, lxml, sqlobject, loguru, python-crontab
6. Создать файл настроек (скопировать example_config.ini > config.ini) и указать необходимые настройки
7. Создать пустую БД
8. Запустить shedules
9. Запустить веб-сервер flask

### Настройка виртуального окружения Pipenv и установка необходимых модулей

Для работы с проектом необходимо установить библиотеки которые он использует и настроить т.н. виртуальное рабочее окружение или virtualenv, для этого используется утилита Pipenv

Если не установлен pipenv, выполнить

```cmd
python -m pip install pipenv
```

Создать виртуальное окружение в директории с проектом

```cmd
pipenv shell
````

Установить все требуемые библиотеки из Pipfile

```cmd
pipenv install --ignore-pipfile
```

### Настройка

Создать файл config.ini (используя example_config.ini)

В секцию `[USER]` добавить логин и пароль пользователя под которым парсер будет авторизовываться на портале dnevnik/ru

В секции `[PARAMETERS]` указать глубину (в днях) на которую парсер должен загружать данные

### Создание пустой БД

```cmd
pipenv run python .\manage.py --database create
```

для удаления БД

```cmd
pipenv run python .\manage.py --database delete
```

### Установка задания для cron

```cmd
pipenv run python schedules.py
```

### Запуск веб-сервера Flask в Linux

```cmd
export FLASK_APP=server
```

```cmd
export FLASK_ENV=development
```

```cmd
flask run
```

### Запуск веб-сервера через Gunicorn

```cmd
gunicorn --bind 0.0.0.0:5000 server:app
```

### Запуск веб-сервера Flask в Windows

```cmd
$env:FLASK_APP = "server"
```

```cmd
$env:FLASK_ENV = "development"
```

```cmd
flask run
```
