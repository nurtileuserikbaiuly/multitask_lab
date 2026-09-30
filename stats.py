import pandas as pd
from scipy import stats

from config import ALPHA


class CorrelationAnalysis:
    """Relationship between two numeric variables: X (tabs) and Y (words)."""

    def __init__(self, x, y, alpha=ALPHA):
        data = pd.DataFrame({"x": x, "y": y}).dropna()
        if len(data) < 3:
            raise ValueError("At least 3 observations are needed for the analysis.")
        if data["x"].nunique() < 2 or data["y"].nunique() < 2:
            raise ValueError("X and Y values must not all be the same.")

        self.x = data["x"].astype(float)
        self.y = data["y"].astype(float)
        self.alpha = alpha
        self.n = len(data)

    def describe(self):
        """Descriptive statistics: n, mean, median, min, max, standard deviation."""
        rows = {}
        for name, s in (("X", self.x), ("Y", self.y)):
            rows[name] = {
                "n": len(s),
                "mean": s.mean(),
                "median": s.median(),
                "min": s.min(),
                "max": s.max(),
                "std": s.std(ddof=1),
            }
        return pd.DataFrame(rows).T

    def regression(self):
        """Linear regression Y = intercept + slope * X, plus r, R squared and p."""
        res = stats.linregress(self.x, self.y)
        return {
            "slope": res.slope,
            "intercept": res.intercept,
            "r": res.rvalue,
            "r2": res.rvalue ** 2,
            "p": res.pvalue,
        }

    def hypothesis_test(self):
        """Test of H0: rho = 0 against H1: rho != 0 (t-test for correlation)."""
        reg = self.regression()
        r = reg["r"]
        df = self.n - 2
        t = r * (df / (1 - r ** 2)) ** 0.5
        p = reg["p"]
        return {
            "t": t,
            "df": df,
            "p": p,
            "alpha": self.alpha,
            "significant": p < self.alpha,
        }

    def confidence_interval(self, which="y", level=0.95):
        """Confidence interval for the mean of X or Y."""
        s = self.y if which == "y" else self.x
        low, high = stats.t.interval(
            level, self.n - 1, loc=s.mean(), scale=stats.sem(s)
        )
        return low, high

    @staticmethod
    def strength(r):
        """Verbal description of the strength of the relationship."""
        a = abs(r)
        if a < 0.1:
            return "negligible"
        if a < 0.3:
            return "weak"
        if a < 0.7:
            return "moderate"
        return "strong"

    def conclusion(self):
        """Automatic written conclusion."""
        reg = self.regression()
        test = self.hypothesis_test()
        r = reg["r"]
        direction = "positive" if r > 0 else "negative"

        if test["significant"]:
            main = (
                f"Since p = {test['p']:.3f} < α = {self.alpha:.2f}, the hypothesis "
                f"of no relationship is rejected: a statistically significant "
                f"{direction} relationship was found ({self.strength(r)}, r = {r:.3f})."
            )
        else:
            main = (
                f"Since p = {test['p']:.3f} ≥ α = {self.alpha:.2f}, the hypothesis "
                f"of no relationship is not rejected: no statistically significant "
                f"relationship was found (r = {r:.3f}, {self.strength(r)})."
            )

        caveat = (
            " Correlation does not prove causation, and a lack of significance "
            "does not prove that there is no relationship: the sample may be too small."
        )
        return main + caveat