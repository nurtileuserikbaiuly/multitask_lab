import numpy as np
import pandas as pd
from scipy import stats

# Names of the factors used in the multiple regression
PREDICTOR_LABELS = {
    "tabs": "Open tabs and apps",
    "sleep_hours": "Hours of sleep",
    "caffeine": "Caffeine today (1 = yes)",
    "fatigue": "Tiredness (1-5)",
}


def compare_two_groups(values_a, values_b):
    """Welch t-test: do two groups have different mean results?"""
    a = pd.Series(values_a).dropna().astype(float)
    b = pd.Series(values_b).dropna().astype(float)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("Each group needs at least 2 participants.")

    v1 = a.var(ddof=1) / len(a)
    v2 = b.var(ddof=1) / len(b)
    if v1 + v2 == 0:
        raise ValueError("All values in both groups are the same.")

    t = (a.mean() - b.mean()) / (v1 + v2) ** 0.5
    df = (v1 + v2) ** 2 / (v1 ** 2 / (len(a) - 1) + v2 ** 2 / (len(b) - 1))
    p = 2 * stats.t.sf(abs(t), df)
    return {
        "n_a": len(a),
        "n_b": len(b),
        "mean_a": a.mean(),
        "mean_b": b.mean(),
        "sd_a": a.std(ddof=1),
        "sd_b": b.std(ddof=1),
        "t": t,
        "df": df,
        "p": p,
    }


def multiple_regression(df, predictors, outcome="words_correct"):
    """Multiple linear regression: outcome = b0 + b1*x1 + b2*x2 + ..."""
    data = df[predictors + [outcome]].dropna()
    n, k = len(data), len(predictors)
    if n < k + 3:
        raise ValueError(f"At least {k + 3} complete responses are needed.")

    y = data[outcome].astype(float).to_numpy()
    X = np.column_stack([np.ones(n), data[predictors].astype(float).to_numpy()])
    if np.linalg.matrix_rank(X) < k + 1:
        raise ValueError(
            "Some factors do not vary or are perfectly related to each other."
        )

    total = ((y - y.mean()) ** 2).sum()
    if total == 0:
        raise ValueError("All results are the same.")

    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residuals = y - X @ beta
    rss = (residuals ** 2).sum()
    if rss < 1e-12:
        raise ValueError("The model fits perfectly, which is not realistic.")

    df_resid = n - k - 1
    sigma2 = rss / df_resid
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df_resid)

    r2 = 1 - rss / total
    adj_r2 = 1 - (1 - r2) * (n - 1) / df_resid
    f_stat = (r2 / k) / ((1 - r2) / df_resid)
    p_f = stats.f.sf(f_stat, k, df_resid)

    names = ["Intercept"] + [PREDICTOR_LABELS.get(c, c) for c in predictors]
    table = pd.DataFrame(
        {"Coefficient": beta, "Std. error": se, "t": t, "p-value": p},
        index=names,
    )
    return {
        "table": table,
        "n": n,
        "df_resid": df_resid,
        "r2": r2,
        "adj_r2": adj_r2,
        "f": f_stat,
        "p_f": p_f,
    }