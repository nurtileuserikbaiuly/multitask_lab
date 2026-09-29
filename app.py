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
    st.session_state.sleep = 7.0
    st.session_state.caffeine = 0
    st.session_state.fatigue = 3
    st.session_state.score = 0

stage = st.session_state.stage

st.title("🧠 MultiTask Lab")

# ---------- Экран 1: согласие ----------
if stage == "consent":
    st.write(
        "Исследование: влияет ли многозадачность "
        "(много открытых вкладок и приложений) на кратковременную память?"
    )
    st.write(
        "Участие добровольное и анонимное. Имя и другие личные данные не собираются: "
        "сохраняются только ответы на несколько вопросов и результат теста."
    )
    if st.button("Согласен, начать"):
        st.session_state.stage = "questions"
        st.rerun()

# ---------- Экран 2: вопросы ----------
elif stage == "questions":
    st.subheader("Несколько вопросов о тебе")

    tabs = st.number_input(
        "Сколько вкладок или приложений у тебя обычно открыто одновременно, "
        "когда ты учишься? (на телефоне и компьютере вместе)",
        min_value=0,
        max_value=50,
        value=1,
        step=1,
    )
    sleep = st.number_input(
        "Сколько часов ты спал(а) прошлой ночью?",
        min_value=0.0,
        max_value=14.0,
        value=7.0,
        step=0.5,
    )
    caffeine = st.radio(
        "Пил(а) ли ты сегодня кофе, крепкий чай или энергетик?",
        ["Нет", "Да"],
        horizontal=True,
    )
    fatigue = st.slider(
        "Насколько ты устал(а) сейчас? (1 - бодр, 5 - очень устал)",
        min_value=1,
        max_value=5,
        value=3,
    )

    if st.button("Далее"):
        st.session_state.tabs = int(tabs)
        st.session_state.sleep = float(sleep)
        st.session_state.caffeine = 1 if caffeine == "Да" else 0
        st.session_state.fatigue = int(fatigue)
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
        db.add_response(
            tabs=st.session_state.tabs,
            words_correct=score,
            source="site",
            sleep_hours=st.session_state.sleep,
            caffeine=st.session_state.caffeine,
            fatigue=st.session_state.fatigue,
        )
        st.session_state.score = score
        st.session_state.stage = "result"
        st.rerun()

# ---------- Экран 6: результат ----------
elif stage == "result":
    st.success(
        f"Ты вспомнил {st.session_state.score} слов из {len(WORDS)}. Спасибо за участие!"
    )
    st.caption(f"Ответов с сайта: {db.count('site')}")
    if st.button("Новый участник"):
        st.session_state.stage = "consent"
        st.rerun()