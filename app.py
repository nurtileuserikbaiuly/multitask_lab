import random
import time

import streamlit as st

from config import WORDS, MEMORIZE_SECONDS
from database import Database
from logic import WordTest

# Page settings
st.set_page_config(
    page_title="MultiTask Lab",
    page_icon="🧠",
    layout="centered",
)

# Custom CSS for the buttons
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #ff4b4b;
        color: white;
    }
    .stButton button:hover {
        background-color: #ff2b2b;
    }
    </style>
""",
    unsafe_allow_html=True,
)

db = Database()
test = WordTest()

STAGES = ["consent", "questions", "ready", "memorize", "recall", "result"]

# Remember which screen the participant is on
if "stage" not in st.session_state:
    st.session_state.stage = "consent"
    st.session_state.tabs = 0
    st.session_state.sleep = 7.0
    st.session_state.caffeine = 0
    st.session_state.fatigue = 3
    st.session_state.score = 0
    st.session_state.word_order = list(WORDS)

stage = st.session_state.stage

st.title("🧠 MultiTask Lab")

# Progress bar: shows how far the participant is
position = STAGES.index(stage)
st.progress(
    position / (len(STAGES) - 1),
    text=f"Step {position + 1} of {len(STAGES)}",
)
st.markdown("---")

# ---------- Screen 1: consent ----------
if stage == "consent":
    st.subheader("Welcome to the Experimental Study!")
    st.info(
        "**Research Question:** Does digital multitasking "
        "(having many open tabs and apps) affect short-term memory?"
    )
    st.write(
        "Participation is voluntary and anonymous. No name or other personal data "
        "is collected: only your answers to a few questions and your test result "
        "are saved."
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("I agree, let's start"):
        st.session_state.stage = "questions"
        st.rerun()

# ---------- Screen 2: questions ----------
elif stage == "questions":
    st.subheader("📋 Participant Questionnaire")
    st.write("Please answer a few quick questions about your current study session.")

    # No default values here: a pre-filled number would push the answers
    # towards that number, so the participant must type their own.
    tabs = st.number_input(
        "How many tabs or apps do you usually have open at the same time "
        "while studying? (phone and computer together)",
        min_value=0,
        max_value=50,
        value=None,
        step=1,
        placeholder="Type a number",
    )
    sleep = st.number_input(
        "How many hours did you sleep last night?",
        min_value=0.0,
        max_value=14.0,
        value=None,
        step=0.5,
        placeholder="Type a number",
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

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Next ➡️"):
        if tabs is None or sleep is None:
            st.warning("Please answer all the questions before you continue.")
        else:
            st.session_state.tabs = int(tabs)
            st.session_state.sleep = float(sleep)
            st.session_state.caffeine = 1 if caffeine == "Yes" else 0
            st.session_state.fatigue = int(fatigue)
            st.session_state.stage = "ready"
            st.rerun()

# ---------- Screen 3: get ready ----------
elif stage == "ready":
    st.subheader("🎯 Memory Test Instructions")
    st.warning(
        f"In a moment, **{len(WORDS)} words** will appear for "
        f"**{MEMORIZE_SECONDS} seconds**. "
        "Try to remember as many as you can.\n\n"
        "⚠️ **Do not write them down on paper or notes.**"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("I'm ready, show the words"):
        # Same words for everyone, but in a random order for each participant
        st.session_state.word_order = random.sample(WORDS, len(WORDS))
        st.session_state.stage = "memorize"
        st.rerun()

# ---------- Screen 4: memorize ----------
elif stage == "memorize":
    st.subheader("👀 Memorize these words:")

    cols = st.columns(3)
    for i, word in enumerate(st.session_state.word_order):
        cols[i % 3].markdown(f"### 🔹 {word}")

    st.markdown("---")
    timer = st.empty()
    for left in range(MEMORIZE_SECONDS, 0, -1):
        timer.error(f"⏳ Seconds left: {left}")
        time.sleep(1)

    st.session_state.stage = "recall"
    st.rerun()

# ---------- Screen 5: recall ----------
elif stage == "recall":
    st.subheader("✍️ Recall Phase")
    answer = st.text_area(
        "Type the words you remember (separated by commas or new lines):",
        height=150,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Submit answer"):
        if not answer.strip():
            st.warning(
                "Please type at least one word. "
                "If you remember nothing, write: none"
            )
        else:
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
    st.balloons()
    st.success(
        f"🎉 You remembered **{st.session_state.score}** words out of {len(WORDS)}. "
        "Thank you for taking part!"
    )
    st.caption(f"📊 Website responses so far: {db.count('site')}")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("New participant"):
        st.session_state.stage = "consent"
        st.rerun()