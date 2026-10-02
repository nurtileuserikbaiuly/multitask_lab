import streamlit as st

from charts import scatter_with_line
from database import Database
from extra_stats import compare_two_groups, multiple_regression
from stats import CorrelationAnalysis

st.set_page_config(page_title="Additional analysis", page_icon="🔬")

st.title("🔬 Additional analysis")
st.caption(
    "The main question (tabs and memory) is answered on the Results page. "
    "Here we check whether other factors matter too: sleep, caffeine and "
    "tiredness. Only website responses are used, because the original survey "
    "did not collect these answers."
)

db = Database()
df = db.get_all("site")

alpha = st.radio(
    "Significance level α",
    [0.01, 0.05, 0.10],
    index=1,
    horizontal=True,
    format_func=lambda a: f"{a:.2f}",
)
adjusted = alpha / 3

st.write(f"Website participants: **{len(df)}**")

if len(df) < 10:
    st.info(
        "Not enough website responses yet. Collect at least 10 responses "
        "(ideally 100 or more) and come back."
    )
    st.stop()

st.warning(
    "Three separate checks are made below (sleep, tiredness, caffeine). "
    "The more checks are made, the higher the chance that one of them looks "
    f"significant by luck, so a stricter threshold is shown too: α / 3 = "
    f"{adjusted:.4f} (Bonferroni correction)."
)


def verdict(p):
    """One-line summary of a p-value."""
    first = "significant" if p < alpha else "not significant"
    second = "significant" if p < adjusted else "not significant"
    return (
        f"p = {p:.3f}: {first} at α = {alpha:.2f}, "
        f"{second} after the correction (α / 3 = {adjusted:.4f})."
    )


def correlation_block(column, title, xlabel):
    """Correlation of one factor with the number of words remembered."""
    st.subheader(title)
    try:
        analysis = CorrelationAnalysis(
            df[column], df["words_correct"], alpha=alpha
        )
    except ValueError as error:
        st.info(f"Cannot be calculated yet: {error}")
        return

    reg = analysis.regression()
    c1, c2, c3 = st.columns(3)
    c1.metric("Participants", analysis.n)
    c2.metric("Correlation r", f"{reg['r']:.3f}")
    c3.metric("p-value", f"{reg['p']:.3f}")
    st.markdown(
        f"**Words = {reg['intercept']:.3f} + {reg['slope']:.3f}·X**, "
        f"R² = {reg['r2']:.3f}. Strength of the relationship: "
        f"{analysis.strength(reg['r'])}."
    )
    st.write(verdict(reg["p"]))
    st.plotly_chart(
        scatter_with_line(
            analysis.x,
            analysis.y,
            reg["slope"],
            reg["intercept"],
            xlabel,
            "Words remembered (Y)",
            reg["r"],
        ),
        width="stretch",
    )


# ---------- 1. Sleep ----------
correlation_block("sleep_hours", "1. Sleep and memory", "Hours of sleep (X)")

# ---------- 2. Tiredness ----------
correlation_block(
    "fatigue", "2. Tiredness and memory", "Tiredness, 1 = alert, 5 = very tired (X)"
)

# ---------- 3. Caffeine ----------
st.subheader("3. Caffeine and memory")
try:
    result = compare_two_groups(
        df.loc[df["caffeine"] == 1, "words_correct"],
        df.loc[df["caffeine"] == 0, "words_correct"],
    )
    st.table(
        {
            "Group": ["Had caffeine", "No caffeine"],
            "n": [result["n_a"], result["n_b"]],
            "Mean words": [f"{result['mean_a']:.2f}", f"{result['mean_b']:.2f}"],
            "SD": [f"{result['sd_a']:.2f}", f"{result['sd_b']:.2f}"],
        }
    )
    st.write(
        f"Two-sample t-test (Welch): t = {result['t']:.3f}, "
        f"df = {result['df']:.1f}. {verdict(result['p'])}"
    )
except ValueError as error:
    st.info(f"Cannot be calculated yet: {error}")

# ---------- 4. Multiple regression ----------
st.subheader("4. All factors together (multiple regression)")
predictors = ["tabs", "sleep_hours", "caffeine", "fatigue"]

if len(df) < 40:
    st.warning(
        "Multiple regression with four factors needs about 40 participants "
        "at least (ideally 100). With fewer, the results below are unreliable."
    )

try:
    model = multiple_regression(df, predictors)
    st.dataframe(model["table"].round(3))
    st.write(
        f"n = {model['n']}, R² = {model['r2']:.3f}, "
        f"adjusted R² = {model['adj_r2']:.3f}. "
        f"Whole model: F = {model['f']:.2f}, p = {model['p_f']:.3f}."
    )

    tabs_row = model["table"].loc["Open tabs and apps"]
    st.markdown(
        f"**Tabs, with the other factors held constant:** each extra open tab "
        f"is associated with a change of **{tabs_row['Coefficient']:+.3f}** words "
        f"(p = {tabs_row['p-value']:.3f}, "
        f"{'significant' if tabs_row['p-value'] < alpha else 'not significant'} "
        f"at α = {alpha:.2f})."
    )
    st.caption(
        "Each coefficient shows the change in words remembered when this factor "
        "increases by 1 and the other factors stay the same. Association does "
        "not prove causation."
    )
except ValueError as error:
    st.info(f"Cannot be calculated yet: {error}")