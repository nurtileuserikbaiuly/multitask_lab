import numpy as np
import streamlit as st
from scipy import stats as sp

from config import ALPHA
from database import Database
from stats import CorrelationAnalysis

st.set_page_config(page_title="Methods and formulas", page_icon="📐")

st.title("📐 Methods and formulas")
st.write(
    "This page shows every calculation used in the study: the formula, "
    "why we use it, and how it works on real numbers. The numbers in the "
    "worked examples are calculated live from the data you select below."
)

db = Database()

SOURCES = {
    "Original survey (report)": "survey",
    "Website test": "site",
    "All data combined": None,
}
choice = st.radio(
    "Data for the worked examples", list(SOURCES.keys()), horizontal=True
)
df = db.get_all(SOURCES[choice])

if len(df) < 4 or df["tabs"].nunique() < 2 or df["words_correct"].nunique() < 2:
    st.info(
        "Not enough data for the worked examples yet: at least 4 participants "
        "with different values are needed. Choose another data source above."
    )
    st.stop()

# ---------- Calculations (the same ones as on the Results page) ----------
analysis = CorrelationAnalysis(df["tabs"], df["words_correct"], alpha=ALPHA)
x, y, n = analysis.x, analysis.y, analysis.n
desc = analysis.describe()
reg = analysis.regression()
test = analysis.hypothesis_test()

r, b, a, r2 = reg["r"], reg["slope"], reg["intercept"], reg["r2"]
t, dfree, p = test["t"], test["df"], test["p"]

xm, ym = x.mean(), y.mean()
sx, sy = x.std(ddof=1), y.std(ddof=1)
sxy = float(((x - xm) * (y - ym)).sum())
sxx = float(((x - xm) ** 2).sum())
syy = float(((y - ym) ** 2).sum())
t_crit = sp.t.ppf(1 - ALPHA / 2, dfree)

# =====================================================================
st.header("1. Question and hypotheses")
st.write(
    "Question: is the number of tabs and apps a student keeps open at the "
    "same time related to short-term memory (the number of words remembered)?"
)
st.write(
    "Statistics works like a court: until the evidence is strong enough, we "
    "assume that there is no relationship. This is the null hypothesis H₀. "
    "The symbol ρ is the true correlation in all students; r (below) is the "
    "correlation we calculate in our sample."
)
st.latex(r"H_0:\ \rho = 0 \qquad\qquad H_1:\ \rho \neq 0")
st.write(
    f"Significance level α = {ALPHA}: we reject H₀ only if a result at least "
    f"this extreme would happen in less than {ALPHA:.0%} of samples when H₀ "
    "is true. The test is two-sided because we did not assume a direction in advance."
)

# =====================================================================
st.header("2. Data and variables")
st.markdown(
    """
- **X** is the number of tabs and apps open at the same time.
- **Y** is the number of words remembered correctly.
- Every participant gives one pair (X, Y). We need pairs, because we look
  at whether X and Y change together.
- In the original survey a range such as "3-5" was replaced by its midpoint (4)
  and "10+" was taken as 10.
"""
)
st.write(f"In the selected data: **n = {n}** participants.")

# =====================================================================
st.header("3. Descriptive statistics")
st.write(
    "First we describe the data: what a typical participant looks like and how "
    "much participants differ from each other. These numbers are used in all "
    "the formulas below."
)
st.latex(
    r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i \qquad\qquad "
    r"s = \sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}}"
)
st.write(
    "The median is the middle value when the data are sorted. In the standard "
    "deviation s we divide by n − 1, not by n, so that s is an unbiased "
    "estimate of the spread of all students (we estimated the mean from the "
    "same data, which uses up one degree of freedom)."
)
st.latex(
    rf"\bar{{x}} = \frac{{{x.sum():g}}}{{{n}}} = {xm:.2f} \qquad\qquad "
    rf"\bar{{y}} = \frac{{{y.sum():g}}}{{{n}}} = {ym:.2f}"
)
st.table(
    {
        "Variable": ["X (tabs)", "Y (words)"],
        "Mean": [f"{xm:.2f}", f"{ym:.2f}"],
        "Median": [f"{x.median():.2f}", f"{y.median():.2f}"],
        "SD (s)": [f"{sx:.2f}", f"{sy:.2f}"],
        "Min": [f"{x.min():g}", f"{y.min():g}"],
        "Max": [f"{x.max():g}", f"{y.max():g}"],
    }
)

# =====================================================================
st.header("4. Correlation coefficient r (Pearson)")
st.write(
    "Idea: for every participant we check whether their X is above or below "
    "the average, and whether their Y is above or below the average. If the "
    "signs usually agree, the relationship is positive; if they usually "
    "disagree, it is negative; if there is no pattern, r is close to 0. "
    "Dividing by the spreads makes r always lie between −1 and +1."
)
st.latex(
    r"r = \frac{\sum (x_i-\bar{x})(y_i-\bar{y})}"
    r"{\sqrt{\sum (x_i-\bar{x})^2 \cdot \sum (y_i-\bar{y})^2}}"
)
st.latex(
    rf"r = \frac{{{sxy:.2f}}}{{\sqrt{{{sxx:.2f}\cdot {syy:.2f}}}}} = {r:.3f}"
)
st.write(
    f"Result: **r = {r:.3f}**, the relationship is "
    f"**{analysis.strength(r)}** and **{'positive' if r > 0 else 'negative'}**."
)
st.table(
    {
        "|r|": ["below 0.1", "0.1 to 0.3", "0.3 to 0.7", "0.7 and above"],
        "Strength": ["negligible", "weak", "moderate", "strong"],
    }
)

# =====================================================================
st.header("5. Linear regression")
st.write(
    "r tells us how strong the relationship is. Regression gives the straight "
    "line that passes best through the points (the least squares line), so we "
    "can say how much Y changes when X increases by 1."
)
st.latex(
    r"b = \frac{\sum (x_i-\bar{x})(y_i-\bar{y})}{\sum (x_i-\bar{x})^2} "
    r"= r\,\frac{s_y}{s_x} \qquad\qquad a = \bar{y} - b\,\bar{x}"
)
st.latex(
    rf"b = \frac{{{sxy:.2f}}}{{{sxx:.2f}}} = {b:.3f} \qquad\qquad "
    rf"a = {ym:.3f} - ({b:.3f})\cdot {xm:.3f} = {a:.3f}"
)
st.latex(rf"\hat{{y}} = {a:.3f} {b:+.3f}\,x")
st.write(
    f"Reading: with 0 tabs we expect about {a:.2f} words, and every extra tab "
    f"goes with a change of {b:+.3f} words on average."
)
st.latex(rf"R^2 = r^2 = {r:.3f}^2 = {r2:.3f}")
st.write(
    f"R² = {r2:.3f}: the line explains {r2:.1%} of the differences between "
    "participants. The rest is other factors and chance."
)

# =====================================================================
st.header("6. Hypothesis test: is the result just chance?")
st.write(
    "With a different group of students r would be different, just by chance. "
    "So we ask: if there were really no relationship, how often would a random "
    "sample give a correlation like ours? We convert r to a number t that "
    "measures how many steps of random variation r is away from 0."
)
st.latex(r"t = r\sqrt{\frac{n-2}{1-r^2}} \qquad\qquad df = n-2")
st.latex(
    rf"t = {r:.3f}\sqrt{{\frac{{{n}-2}}{{1-{r:.3f}^2}}}} = {t:.3f} "
    rf"\qquad\qquad df = {n}-2 = {dfree}"
)
st.write(
    "The degrees of freedom are n − 2 because two numbers (a and b) were "
    "estimated from the data when we fitted the line."
)
st.latex(r"p = 2\cdot P\left(T_{df} > |t|\right)")
st.latex(
    rf"p = 2\cdot P\left(T_{{{dfree}}} > {abs(t):.3f}\right) = {p:.3f}"
)
st.write(
    f"p is the probability of getting a |t| this large or larger if H₀ is true. "
    f"The critical value at α = {ALPHA} is t = {t_crit:.3f}: if |t| is larger "
    "than it (equivalently, if p < α), the result is too rare to be chance."
)
if test["significant"]:
    st.success(
        f"|t| = {abs(t):.3f} > {t_crit:.3f} and p = {p:.3f} < {ALPHA}: "
        "H₀ is rejected. The relationship is statistically significant."
    )
else:
    st.info(
        f"|t| = {abs(t):.3f} < {t_crit:.3f} and p = {p:.3f} ≥ {ALPHA}: "
        "H₀ is not rejected. No statistically significant relationship was found."
    )
st.caption(
    "Not rejecting H₀ is not the same as proving that there is no relationship: "
    "with a small sample a real relationship can stay hidden."
)

# =====================================================================
st.header("7. Confidence intervals")
st.write(
    "A single number such as r = 0.23 looks more precise than it is. A "
    "confidence interval shows the range of values that is consistent with "
    "the data."
)

st.subheader("For a mean")
st.latex(
    r"\bar{y} \pm t_{1-\alpha/2,\ n-1}\cdot\frac{s}{\sqrt{n}}"
)
t_mean = sp.t.ppf(1 - ALPHA / 2, n - 1)
margin = t_mean * sy / np.sqrt(n)
st.latex(
    rf"{ym:.2f} \pm {t_mean:.3f}\cdot\frac{{{sy:.2f}}}{{\sqrt{{{n}}}}} "
    rf"= {ym:.2f} \pm {margin:.2f} \;\Rightarrow\; "
    rf"({ym - margin:.2f};\ {ym + margin:.2f})"
)

st.subheader("For the correlation r (Fisher transformation)")
st.write(
    "The distribution of r is skewed, so r is first transformed to z, which is "
    "close to normal. The interval is built for z and then transformed back."
)
st.latex(
    r"z = \tfrac{1}{2}\ln\frac{1+r}{1-r} = \operatorname{arctanh}(r) "
    r"\qquad SE = \frac{1}{\sqrt{n-3}} \qquad "
    r"r_{low,\,high} = \tanh\left(z \mp z_{1-\alpha/2}\cdot SE\right)"
)
z = float(np.arctanh(np.clip(r, -0.999999, 0.999999)))
se = 1 / np.sqrt(n - 3)
z_crit = sp.norm.ppf(1 - ALPHA / 2)
r_low, r_high = np.tanh(z - z_crit * se), np.tanh(z + z_crit * se)
st.latex(
    rf"z = {z:.3f} \qquad SE = \frac{{1}}{{\sqrt{{{n}-3}}}} = {se:.3f} "
    rf"\qquad r \in ({r_low:.3f};\ {r_high:.3f})"
)
if r_low < 0 < r_high:
    st.write(
        "The interval contains 0. This is the same conclusion as p ≥ α, but "
        "easier to see: the data cannot tell apart a negative, a zero and a "
        "positive relationship."
    )

# =====================================================================
st.header("8. Robustness checks")

st.subheader("Spearman rank correlation")
st.write(
    "To make sure that the conclusion does not depend on the method, we repeat "
    "the analysis on ranks (1st, 2nd, 3rd ... place) instead of raw values. "
    "Spearman's ρ is the Pearson correlation of the ranks, so it does not "
    "assume a straight-line relationship and is less sensitive to outliers."
)
st.latex(r"\rho_s = r\left(\operatorname{rank}(x),\ \operatorname{rank}(y)\right)")
rho, p_rho = sp.spearmanr(x, y)
st.write(f"Result: ρ = {rho:.3f}, p = {p_rho:.3f}.")

st.subheader("Needed sample size")
st.write(
    "Power is the chance to detect a relationship that really exists. This "
    "formula shows how many participants are needed to detect a correlation of "
    "the observed size with power 80%."
)
st.latex(
    r"n = \left(\frac{z_{1-\alpha/2} + z_{power}}{\operatorname{arctanh}|r|}"
    r"\right)^2 + 3"
)
if abs(r) < 0.05:
    st.write(
        "The observed correlation is almost zero, so the needed sample size "
        "cannot be estimated meaningfully."
    )
else:
    z_power = sp.norm.ppf(0.80)
    needed = int(
        np.ceil(
            ((z_crit + z_power) / np.arctanh(min(abs(r), 0.999999))) ** 2 + 3
        )
    )
    st.latex(
        rf"n = \left(\frac{{{z_crit:.2f} + {z_power:.2f}}}"
        rf"{{\operatorname{{arctanh}}({abs(r):.3f})}}\right)^2 + 3 "
        rf"\approx {needed}"
    )
    st.write(
        f"About **{needed}** participants are needed; the selected data have {n}."
    )

# =====================================================================
st.header("9. Additional analysis (sleep, caffeine, tiredness)")
st.write(
    "These methods are used on the Additional analysis page, with website "
    "responses only."
)

st.subheader("Two groups: Welch t-test")
st.write(
    "Compares the mean result of two groups (for example, with and without "
    "caffeine) and does not assume that the groups have the same spread."
)
st.latex(
    r"t = \frac{\bar{x}_1-\bar{x}_2}{\sqrt{\dfrac{s_1^2}{n_1}+\dfrac{s_2^2}{n_2}}}"
)
st.latex(
    r"df = \frac{\left(\dfrac{s_1^2}{n_1}+\dfrac{s_2^2}{n_2}\right)^2}"
    r"{\dfrac{(s_1^2/n_1)^2}{n_1-1}+\dfrac{(s_2^2/n_2)^2}{n_2-1}}"
)

st.subheader("Several factors together: multiple regression")
st.write(
    "A single correlation can be misleading if another factor affects both "
    "variables (for example, little sleep may go with many open tabs and with "
    "poor memory). Multiple regression estimates the effect of each factor "
    "while the other factors are held constant."
)
st.latex(
    r"y = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \dots + \beta_k x_k + \varepsilon"
    r"\qquad \hat{\beta} = (X^{T}X)^{-1}X^{T}y"
)
st.latex(
    r"\hat{\sigma}^2 = \frac{RSS}{n-k-1} \qquad "
    r"SE(\hat{\beta}_j) = \sqrt{\hat{\sigma}^2\left[(X^{T}X)^{-1}\right]_{jj}} "
    r"\qquad t_j = \frac{\hat{\beta}_j}{SE(\hat{\beta}_j)}"
)
st.latex(
    r"R^2 = 1-\frac{RSS}{TSS} \qquad "
    r"R^2_{adj} = 1-(1-R^2)\frac{n-1}{n-k-1} \qquad "
    r"F = \frac{R^2/k}{(1-R^2)/(n-k-1)}"
)
st.write(
    "RSS is the sum of squared errors of the model, TSS is the total sum of "
    "squares of y, k is the number of factors. The adjusted R² is lower than "
    "R² and does not grow just because more factors were added."
)

st.subheader("Many tests: Bonferroni correction")
st.write(
    "The more tests we run, the higher the chance that one of them looks "
    "significant by luck. With m tests we use a stricter threshold."
)
st.latex(r"\alpha_{adj} = \frac{\alpha}{m}")

# =====================================================================
st.header("10. Assumptions and how we checked them")
st.table(
    {
        "Assumption of Pearson's r": [
            "The relationship is roughly a straight line",
            "No extreme outliers",
            "Each participant counted once, independent answers",
            "Variables are numeric",
        ],
        "How we check it": [
            "Scatter plot on the Results page",
            "Scatter plot and histograms",
            "Anonymous, one test per participant (asked in the invitation)",
            "Counts of tabs and words",
        ],
    }
)
st.write(
    "If an assumption is doubtful, the Spearman correlation (section 8) is "
    "the safer check, and in this study it gives the same conclusion as r "
    "when the data are the original survey."
)

# =====================================================================
st.header("11. How the program does it")
st.table(
    {
        "Step": [
            "Mean, median, SD",
            "r, slope, intercept, R²",
            "t statistic and p-value",
            "Confidence intervals",
            "Spearman correlation",
            "Welch t-test",
            "Multiple regression",
        ],
        "Method in the code": [
            "pandas: mean, median, std with n − 1",
            "SciPy: linregress (least squares)",
            "formula from section 6, p from the t distribution (SciPy)",
            "SciPy: t distribution; Fisher transformation with NumPy",
            "SciPy: spearmanr",
            "formula from section 9, p from the t distribution",
            "matrix formula with NumPy, p-values from the t and F distributions",
        ],
    }
)
st.write(
    "The same calculations reproduce every number of the original report "
    "(r = 0.230, R² = 0.053, t = 1.340, df = 32, p = 0.190), and the "
    "multiple regression was cross-checked against a standard statistics "
    "library."
)

# =====================================================================
st.header("12. How to read the result")
st.markdown(
    """
- **We can say:** whether a statistically significant relationship was found in this sample.
- **We cannot say:** that there is no relationship (a small sample can hide one), or that one thing causes the other (correlation is not causation).
- **Always look at three things together:** the size of the effect (r, b), the uncertainty (confidence interval, p-value) and the sample size.
"""
)