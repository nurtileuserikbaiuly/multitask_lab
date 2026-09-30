import streamlit as st

from charts import histogram, scatter_with_line
from database import Database
from stats import CorrelationAnalysis

st.set_page_config(page_title="Результаты", page_icon="📊")

st.title("📊 Результаты исследования")

db = Database()

SOURCES = {
    "Опрос из отчёта": "survey",
    "Тест на сайте": "site",
    "Все данные вместе": None,
}

choice = st.radio("Какие данные анализировать?", list(SOURCES.keys()), horizontal=True)
alpha = st.radio(
    "Уровень значимости α",
    [0.01, 0.05, 0.10],
    index=1,
    horizontal=True,
    format_func=lambda a: f"{a:.2f}",
)

df = db.get_all(SOURCES[choice])
st.write(f"Участников: **{len(df)}**")

if choice == "Все данные вместе":
    st.warning(
        "Данные опроса из отчёта измерены менее точно (диапазоны заменены серединой, "
        "слова записаны со слов респондентов), поэтому объединять их с тестом на сайте "
        "нужно осторожно."
    )

if len(df) < 3 or df["tabs"].nunique() < 2 or df["words_correct"].nunique() < 2:
    st.info(
        "Пока недостаточно данных для анализа: нужно минимум 3 участника "
        "с разными значениями."
    )
    st.stop()

analysis = CorrelationAnalysis(df["tabs"], df["words_correct"], alpha=alpha)
desc = analysis.describe()
reg = analysis.regression()
test = analysis.hypothesis_test()

# ---------- Главные цифры ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Среднее X (вкладки)", f"{desc.loc['X', 'mean']:.2f}")
c2.metric("Среднее Y (слова)", f"{desc.loc['Y', 'mean']:.2f}")
c3.metric("Корреляция r", f"{reg['r']:.3f}")
c4.metric("p-value", f"{test['p']:.3f}")

# ---------- Описательная статистика ----------
st.subheader("Описательная статистика")
table = desc.rename(
    index={"X": "X: вкладки", "Y": "Y: слова"},
    columns={
        "n": "n",
        "mean": "Среднее",
        "median": "Медиана",
        "min": "Мин",
        "max": "Макс",
        "std": "σ",
    },
)
st.dataframe(table.round(2))

# ---------- Графики ----------
st.subheader("Графики")
g1, g2 = st.columns(2)
g1.plotly_chart(
    histogram(analysis.x, "Вкладки и приложения (X)", "Число вкладок"),
    width="stretch",
)
g2.plotly_chart(
    histogram(analysis.y, "Запомненные слова (Y)", "Число слов"),
    width="stretch",
)
st.plotly_chart(
    scatter_with_line(
        analysis.x,
        analysis.y,
        reg["slope"],
        reg["intercept"],
        "Число вкладок (X)",
        "Запомненные слова (Y)",
        reg["r"],
    ),
    width="stretch",
)

# ---------- Регрессия и проверка гипотезы ----------
st.subheader("Регрессия")
st.markdown(
    f"**Y = {reg['intercept']:.3f} + {reg['slope']:.3f}·X**, R² = {reg['r2']:.3f}"
)

st.subheader("Проверка гипотезы")
st.write(
    f"H₀: ρ = 0 (связи нет), H₁: ρ ≠ 0. Уровень значимости α = {alpha:.2f}. "
    f"t = {test['t']:.3f}, df = {test['df']}, p = {test['p']:.3f}."
)
low, high = analysis.confidence_interval("y")
st.write(f"95% доверительный интервал для среднего числа слов: от {low:.2f} до {high:.2f}.")

# ---------- Вывод ----------
st.subheader("Вывод")
st.info(analysis.conclusion())

# ---------- Скачивание ----------
st.download_button(
    "Скачать данные (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name="multitask_data.csv",
    mime="text/csv",
)