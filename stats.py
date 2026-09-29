import pandas as pd
from scipy import stats

from config import ALPHA


class CorrelationAnalysis:
    """Связь между двумя числовыми переменными: X (вкладки) и Y (слова)."""

    def __init__(self, x, y, alpha=ALPHA):
        data = pd.DataFrame({"x": x, "y": y}).dropna()
        if len(data) < 3:
            raise ValueError("Для анализа нужно минимум 3 наблюдения.")
        if data["x"].nunique() < 2 or data["y"].nunique() < 2:
            raise ValueError("Значения X и Y не должны быть все одинаковыми.")

        self.x = data["x"].astype(float)
        self.y = data["y"].astype(float)
        self.alpha = alpha
        self.n = len(data)

    def describe(self):
        """Описательная статистика: n, среднее, медиана, min, max, σ."""
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
        """Линейная регрессия Y = intercept + slope * X, а также r, R², p."""
        res = stats.linregress(self.x, self.y)
        return {
            "slope": res.slope,
            "intercept": res.intercept,
            "r": res.rvalue,
            "r2": res.rvalue ** 2,
            "p": res.pvalue,
        }

    def hypothesis_test(self):
        """Проверка H0: ρ = 0 против H1: ρ != 0 (t-тест для корреляции)."""
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
        """Доверительный интервал для среднего X или Y."""
        s = self.y if which == "y" else self.x
        low, high = stats.t.interval(
            level, self.n - 1, loc=s.mean(), scale=stats.sem(s)
        )
        return low, high

    @staticmethod
    def strength(r):
        """Словесное описание силы связи."""
        a = abs(r)
        if a < 0.1:
            return "практически отсутствует"
        if a < 0.3:
            return "слабая"
        if a < 0.7:
            return "умеренная"
        return "сильная"

    def conclusion(self):
        """Автоматический текстовый вывод."""
        reg = self.regression()
        test = self.hypothesis_test()
        r = reg["r"]
        direction = "положительная" if r > 0 else "отрицательная"

        if test["significant"]:
            main = (
                f"Так как p = {test['p']:.3f} < α = {self.alpha}, гипотеза об "
                f"отсутствии связи отвергается: найдена статистически значимая "
                f"{direction} связь ({self.strength(r)}, r = {r:.3f})."
            )
        else:
            main = (
                f"Так как p = {test['p']:.3f} ≥ α = {self.alpha}, гипотеза об "
                f"отсутствии связи не отвергается: статистически значимой связи "
                f"не найдено (r = {r:.3f}, {self.strength(r)})."
            )

        caveat = (
            " Корреляция не доказывает причинность, а отсутствие значимости "
            "не доказывает, что связи нет: возможно, выборка мала."
        )
        return main + caveat