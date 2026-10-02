import numpy as np

from database import Database

db = Database()

if db.remote is not None:
    print("СТОП: подключён Supabase. Демо-данные нельзя добавлять в настоящую базу.")
    print("Переименуй .streamlit/secrets.toml в secrets.toml.off и запусти скрипт снова.")
    raise SystemExit

if db.count("site") > 0:
    print("В data.db уже есть ответы с сайта, демо-данные не добавлены.")
    raise SystemExit

rng = np.random.default_rng(1)
for _ in range(60):
    tabs = int(rng.integers(0, 12))
    sleep = float(np.round(rng.uniform(4, 9) * 2) / 2)
    caffeine = int(rng.integers(0, 2))
    fatigue = int(rng.integers(1, 6))
    words = 6 + 0.1 * (sleep - 6) - 0.15 * tabs + 0.8 * caffeine - 0.3 * (fatigue - 3)
    words = int(np.clip(round(words + rng.normal(0, 1.5)), 0, 15))
    db.add_response(
        tabs=tabs,
        words_correct=words,
        source="site",
        sleep_hours=sleep,
        caffeine=caffeine,
        fatigue=fatigue,
    )

print("Добавлено 60 ДЕМО-ответов (выдуманные данные, только для проверки страницы).")
print("После проверки удали data.db и снова выполни: python import_survey.py")