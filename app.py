import time

import streamlit as st

from config import WORDS, MEMORIZE_SECONDS
from database import Database
from logic import WordTest

st.set_page_config(page_title="MultiTask Lab", page_icon="🧠")

db = Database()
test = WordTest()

# Запоминаем, на каком экране находится студент
if "stage" not in st.session_state:
    st.session_state.stage = "consent"
    st.session_state.tabs = 0
    st.session_state.score = 0

stage = st.session_state.stage

st.title("🧠 MultiTask Lab")

# ---------- Экран 1: согласие ----------
if stage == "consent":
    st.write("Исследование: влияет ли многозадачность на кратковременную память?")
    st.write(
        "Участие добровольное. Личные данные не собираются: "
        "сохраняются только число вкладок и результат теста."
    )
    if st.button("Согласен, начать"):
        st.session_state.stage = "tabs"
        st.rerun()

# ---------- Экран 2: вопрос про вкладки ----------
elif stage == "tabs":
    tabs = st.number_input(
        "Сколько вкладок или приложений у тебя обычно открыто, когда ты учишься?",
        min_value=0,
        max_value=50,
        value=1,
        step=1,
    )
    if st.button("Далее"):
        st.session_state.tabs = int(tabs)
        st.session_state.stage = "ready"
        st.rerun()

# ---------- Экран 3: подготовка ----------
elif stage == "ready":
    st.write(
        f"Сейчас на {MEMORIZE_SECONDS} секунд появятся {len(WORDS)} слов. "
        "Постарайся запомнить как можно больше. "
        "Записывать их нельзя."
    )
    if st.button("Я готов, показать слова"):
        st.session_state.stage = "memorize"
        st.rerun()

# ---------- Экран 4: запоминание ----------
elif stage == "memorize":
    cols = st.columns(3)
    for i, word in enumerate(WORDS):
        cols[i % 3].markdown(f"### {word}")

    timer = st.empty()
    for left in range(MEMORIZE_SECONDS, 0, -1):
        timer.metric("Осталось секунд", left)
        time.sleep(1)

    st.session_state.stage = "recall"
    st.rerun()

# ---------- Экран 5: ответ ----------
elif stage == "recall":
    answer = st.text_area(
        "Напиши слова, которые запомнил (через запятую или с новой строки):",
        height=200,
    )
    if st.button("Отправить ответ"):
        score = test.count_correct(answer)
        db.add_response(st.session_state.tabs, score)
        st.session_state.score = score
        st.session_state.stage = "result"
        st.rerun()

# ---------- Экран 6: результат ----------
elif stage == "result":
    st.success(
        f"Ты вспомнил {st.session_state.score} слов из {len(WORDS)}. Спасибо за участие!"
    )
    st.caption(f"Всего участников: {db.count()}")
    if st.button("Новый участник"):
        st.session_state.stage = "consent"
        st.rerun()