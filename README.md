# mongo-aiogram-test-case
Бот для получения аггрегированных данных из mongodb.
# Стек
mongodb (motor), aiogram, asyncio.
# Запуск
1. Клонировать репозиторий. Для удобства добавлен скрипт для запуска контейнера с mongodb и восстановлением туда данных из дампа: `sh ./mongo-run.sh`
2. Создать файл .env с токеном телеграм-бота. Пример - в `example.env`
3. Создать и активировать виртуальное окружение:
```
python -m venv venv
source /venv/bin/activate
```
4. Установить зависимости: `pip install -r requirements.txt`
5. Запустить бота: `python bot.py`
# Примеры запросов
```
{"dt_from": "2022-09-01T00:00:00", "dt_upto": "2022-12-31T23:59:00", "group_type": "month"}
{"dt_from": "2022-10-01T00:00:00", "dt_upto": "2022-11-30T23:59:00", "group_type": "day"}
{"dt_from": "2022-02-01T00:00:00", "dt_upto": "2022-02-02T00:00:00", "group_type": "hour"}
```
