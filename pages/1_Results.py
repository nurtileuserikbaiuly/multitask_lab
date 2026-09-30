import streamlit as st

from charts import histogram, scatter_with_line
from database import Database
from stats import CorrelationAnalysis

st.set_page_config(page_title="Results", page_icon="📊")

st.title("📊 Study results")

db = Database()

SOURCES = {
    "Original survey (report)": "survey",
    "Website test": "site",
    "All data combined": None,
}

choice = st.radio("Which data do you want to analyse?", list(SOURCES.keys()), horizontal=True)
alpha = st.radio(
    "Significance level α",
    [0.01, 0.05, 0.10],
    index=1,
    horizontal=True,
    format_func=lambda a: f"{a:.2f}",
)

df = db.get_all(SOURCES[choice])
st.write(f"Participants: **{len(df)}**")

if choice == "All data combined":
    st.warning(
        "The original survey data were measured less precisely (ranges were replaced "
        "by their midpoints and the words were reported by the respondents), so "
        "combining them with the website test should be done with caution."
    )

if len(df) < 3 or df["tabs"].nunique() < 2 or df["words_correct"].nunique() < 2:
    st.info(
        "Not enough data for the analysis yet: at least 3 participants "
        "with different values are needed."
    )
    st.stop()

analysis = CorrelationAnalysis(df["tabs"], df["words_correct"], alpha=alpha)
desc = analysis.describe()
reg = analysis.regression()
test = analysis.hypothesis_test()

# ---------- Key numbers ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean X (tabs)", f"{desc.loc['X', 'mean']:.2f}")
c2.metric("Mean Y (words)", f"{desc.loc['Y', 'mean']:.2f}")
c3.metric("Correlation r", f"{reg['r']:.3f}")
c4.metric("p-value", f"{test['p']:.3f}")

# ---------- Descriptive statistics ----------
st.subheader("Descriptive statistics")
table = desc.rename(
    index={"X": "X: tabs", "Y": "Y: words"},
    columns={
        "n": "n",
        "mean": "Mean",
        "median": "Median",
        "min": "Min",
        "max": "Max",
        "std": "SD",
    },
)
st.dataframe(table.round(2))

# ---------- Charts ----------
st.subheader("Charts")
g1, g2 = st.columns(2)
g1.plotly_chart(
    histogram(analysis.x, "Open tabs and apps (X)", "Number of tabs"),
    width="stretch",
)
g2.plotly_chart(
    histogram(analysis.y, "Words remembered (Y)", "Number of words"),
    width="stretch",
)
st.plotly_chart(
    scatter_with_line(
        analysis.x,
        analysis.y,
        reg["slope"],
        reg["intercept"],
        "Number of tabs (X)",
        "Words remembered (Y)",
        reg["r"],
    ),
    width="stretch",
)

# ---------- Regression and hypothesis test ----------
st.subheader("Regression")
st.markdown(
    f"**Y = {reg['intercept']:.3f} + {reg['slope']:.3f}·X**, R² = {reg['r2']:.3f}"
)

st.subheader("Hypothesis test")
st.write(
    f"H₀: ρ = 0 (no relationship), H₁: ρ ≠ 0. Significance level α = {alpha:.2f}. "
    f"t = {test['t']:.3f}, df = {test['df']}, p = {test['p']:.3f}."
)
low, high = analysis.confidence_interval("y")
st.write(f"95% confidence interval for the mean number of words: from {low:.2f} to {high:.2f}.")

# ---------- Conclusion ----------
st.subheader("Conclusion")
st.info(analysis.conclusion())

# ---------- Download ----------
st.download_button(
    "Download data (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name="multitask_data.csv",
    mime="text/csv",
)