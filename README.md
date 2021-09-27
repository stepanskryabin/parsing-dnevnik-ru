# parsing-dnevik-ru

Утилита предназначена для парсинга расписаний с портала dnevnik.ru. Для парсинга необходим логин и пароль к порталу.

## Запуск в Linux

export FLASK_APP=server
export FLASK_ENV=development
flask run

## Запуск в Windows

$env:FLASK_APP = "server"
$env:FLASK_ENV = "development"
flask run

## Создание БД

pipenv run python ./manager.py --database create

## Удаление БД

pipenv run python ./manager.py --database delete
