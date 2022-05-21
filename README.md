# parsing-dnevik-ru

Программа предназначена для парсинга расписаний с портала dnevnik.ru и последующего вывода расписания на экран терминала (киоска).

Для парсинга данных необходима ссылка с taskId.

##
![Main page](/static/img/screenshot_main_page.png "Main page")

![Timetable page](/static/img/screenshot_timetable_page.png "Timetable page")

## Установка

1. Установить Python версии 3.10 или выше.
2. Клонировать репозиторий git clone https://github.com/stepanskryabin/parsing-dnevnik-ru.git
3. Перейти в директорию parsing-dnevnik-ru
4. Настроить виртуальное окружение pipenv
5. Установить модули: Flask, selenium, beautifulsoup4, lxml, sqlobject, loguru, python-crontab
6. Создать файл настроек (скопировать example_config.ini > config.ini) и указать необходимые настройки
7. Создать пустую БД
8. Скопировать ссылку содержащую taskId в `TASK_ID_URL` (расположенный в разделе `[DNEVNIK_RU]` config.ini).
9. Скопировать в корневую директорию исполняемый файл chromedriver (https://chromedriver.chromium.org/downloads).
10. Запустить парсер
11. Запустить веб-сервер flask

### Настройка виртуального окружения Pipenv и установка необходимых модулей

Для работы с проектом необходимо установить библиотеки которые он использует и настроить т.н. виртуальное рабочее
окружение или virtualenv, для этого используется утилита [Pipenv](https://pipenv.pypa.io/en/latest/)

Если не установлен pipenv, выполнить:

```cmd
python -m pip install pipenv
```

Создать виртуальное окружение в директории с проектом:

```cmd
pipenv shell
````

Установить все требуемые библиотеки из Pipfile:

```cmd
pipenv install --ignore-pipfile
```

### Настройка

Создать файл config.ini (используя example_config.ini)

В секции `[DNEVNIK_RU]` в параметре `TASK_ID_URL` указать url который содержит id сессии авторизации через госуслуги,
например `https://login.dnevnik.ru/esia/auth?taskId=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX&regionId=141`

В секции `[PARAMETERS]` указать глубину (в днях) на которую парсер должен загружать данные

### Создание пустой БД

```cmd
pipenv run python ./manage.py --database create
```

Для удаления БД:

```cmd
pipenv run python ./manage.py --database delete
```

### Установка ChromeDriver

Перед установкой ChromeDriver убедится что установлена свежая версия браузера Google Chrome или Chromium.
После чего скачать архив с ChromeDriver [тут](https://chromedriver.chromium.org/downloads) в соответствии с той версией
браузера которая установлена в системе. Распаковать исполняемый файл chromedriver в корень директории с кодом проекта.

### Запуск парсера

```cmd
pipenv run python ./parser.py
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
