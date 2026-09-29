import os

from database import Database

TEST_FILE = "test_check.db"

db = Database(TEST_FILE)
db.add_response(tabs=3, words_correct=7)
db.add_response(tabs=8, words_correct=5)
db.add_response(tabs=0, words_correct=9)

print("Записей в базе:", db.count())
print(db.get_all())

os.remove(TEST_FILE)
print("Проверка пройдена, тестовый файл удалён.")