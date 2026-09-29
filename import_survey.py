from database import Database

# (X: вкладки/приложения, Y: слова) - данные из отчёта.
# Диапазон -> середина (например, "3-5" -> 4), "N+" -> N.
SURVEY = [
    (1, 1), (2.5, 6), (2.5, 6), (3, 0), (4, 4),
    (4, 6), (3, 7), (3, 5), (3, 4), (3, 8),
    (4, 4), (4.5, 3), (4.5, 8), (4, 4), (5.5, 13),
    (5, 10), (5, 3), (5, 6), (5, 10), (5, 6),
    (6.5, 7), (6, 10), (6.5, 7), (7, 7), (7, 4),
    (8, 8), (8, 5), (8, 5), (10, 5), (10, 4),
    (10, 4), (10, 3), (11, 9), (0, 0),
]

db = Database()

if db.count("survey") > 0:
    print("Данные опроса уже загружены, повторно не добавляю.")
else:
    for tabs, words in SURVEY:
        db.add_response(tabs=tabs, words_correct=words, source="survey")
    print(f"Загружено строк: {len(SURVEY)}")

df = db.get_all("survey")
print("Строк опроса в базе:", len(df))
print("Среднее X (вкладки):", round(df["tabs"].mean(), 2))
print("Среднее Y (слова):", round(df["words_correct"].mean(), 2))