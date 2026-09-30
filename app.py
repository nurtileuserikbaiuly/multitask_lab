import time

import streamlit as st

from config import WORDS, MEMORIZE_SECONDS
from database import Database
from logic import WordTest

st.set_page_config(page_title="MultiTask Lab", page_icon="🧠")

db = Database()
test = WordTest()

# Remember which screen the participant is on
if "stage" not in st.session_state:
    st.session_state.stage = "consent"
    st.session_state.tabs = 0
    st.session_state.sleep = 7.0
    st.session_state.caffeine = 0
    st.session_state.fatigue = 3
    st.session_state.score = 0

stage = st.session_state.stage

st.title("🧠 MultiTask Lab")

# ---------- Screen 1: consent ----------
if stage == "consent":
    st.write(
        "Study: does multitasking "
        "(many open tabs and apps) affect short-term memory?"
    )
    st.write(
        "Participation is voluntary and anonymous. No name or other personal data "
        "is collected: only your answers to a few questions and your test result "
        "are saved."
    )
    if st.button("I agree, let's start"):
        st.session_state.stage = "questions"
        st.rerun()

# ---------- Screen 2: questions ----------
elif stage == "questions":
    st.subheader("A few questions about you")

    tabs = st.number_input(
        "How many tabs or apps do you usually have open at the same time "
        "while studying? (phone and computer together)",
        min_value=0,
        max_value=50,
        value=1,
        step=1,
    )
    sleep = st.number_input(
        "How many hours did you sleep last night?",
        min_value=0.0,
        max_value=14.0,
        value=7.0,
        step=0.5,
    )
    caffeine = st.radio(
        "Have you had coffee, strong tea or an energy drink today?",
        ["No", "Yes"],
        horizontal=True,
    )
    fatigue = st.slider(
        "How tired are you right now? (1 = fully alert, 5 = very tired)",
        min_value=1,
        max_value=5,
        value=3,
    )

    if st.button("Next"):
        st.session_state.tabs = int(tabs)
        st.session_state.sleep = float(sleep)
        st.session_state.caffeine = 1 if caffeine == "Yes" else 0
        st.session_state.fatigue = int(fatigue)
        st.session_state.stage = "ready"
        st.rerun()

# ---------- Screen 3: get ready ----------
elif stage == "ready":
    st.write(
        f"In a moment, {len(WORDS)} words will appear for {MEMORIZE_SECONDS} seconds. "
        "Try to remember as many as you can. "
        "Do not write them down."
    )
    if st.button("I'm ready, show the words"):
        st.session_state.stage = "memorize"
        st.rerun()

# ---------- Screen 4: memorize ----------
elif stage == "memorize":
    cols = st.columns(3)
    for i, word in enumerate(WORDS):
        cols[i % 3].markdown(f"### {word}")

    timer = st.empty()
    for left in range(MEMORIZE_SECONDS, 0, -1):
        timer.metric("Seconds left", left)
        time.sleep(1)

    st.session_state.stage = "recall"
    st.rerun()

# ---------- Screen 5: recall ----------
elif stage == "recall":
    answer = st.text_area(
        "Type the words you remember (separated by commas or new lines):",
        height=200,
    )
    if st.button("Submit answer"):
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

# ---------- Screen 6: result ----------
elif stage == "result":
    st.success(
        f"You remembered {st.session_state.score} words out of {len(WORDS)}. "
        "Thank you for taking part!"
    )
    st.caption(f"Website responses so far: {db.count('site')}")
    if st.button("New participant"):
        st.session_state.stage = "consent"
        st.rerun()