import requests

from database import Database

db = Database()

if db.remote is None:
    print("Supabase не настроен: нет файла .streamlit/secrets.toml.off или в нём нет раздела [supabase].")
else:
    try:
        print("Подключение к Supabase работает. Строк в таблице:", db.count())
    except requests.exceptions.HTTPError as error:
        code = error.response.status_code
        if code in (401, 403):
            print(f"Ошибка {code}: доступ запрещён. Проверь секретный ключ (key) в secrets.toml.off.")
        elif code == 404:
            print("Ошибка 404: таблица responses не найдена. Повтори пункт 8.2 и проверь адрес проекта (url).")
        else:
            print(f"Ошибка сервера {code}:", error.response.text[:200])
    except requests.exceptions.RequestException:
        print("Не удалось подключиться: проверь адрес проекта (url) в secrets.toml.off и интернет.")