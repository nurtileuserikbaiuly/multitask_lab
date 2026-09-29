from database import Database
from stats import CorrelationAnalysis

db = Database()
df = db.get_all("survey")

if df.empty:
    print("В базе нет данных опроса. Сначала выполни: python import_survey.py")
    raise SystemExit

analysis = CorrelationAnalysis(df["tabs"], df["words_correct"])
desc = analysis.describe()
reg = analysis.regression()
test = analysis.hypothesis_test()
ci_low, ci_high = analysis.confidence_interval("y")


def check(name, value, expected, tol):
    status = "OK  " if abs(value - expected) <= tol else "FAIL"
    print(f"{status} {name}: {value:.4f} (в отчёте {expected})")


check("n", analysis.n, 34, 0)
check("среднее X", desc.loc["X", "mean"], 5.43, 0.01)
check("среднее Y", desc.loc["Y", "mean"], 5.65, 0.01)
check("σ X", desc.loc["X", "std"], 2.74, 0.01)
check("σ Y", desc.loc["Y", "std"], 2.88, 0.01)
check("r", reg["r"], 0.230, 0.001)
check("R²", reg["r2"], 0.053, 0.001)
check("наклон", reg["slope"], 0.242, 0.001)
check("свободный член", reg["intercept"], 4.335, 0.001)
check("t", test["t"], 1.340, 0.001)
check("df", test["df"], 32, 0)
check("p", test["p"], 0.190, 0.001)
check("ДИ Y, нижняя граница", ci_low, 4.64, 0.01)
check("ДИ Y, верхняя граница", ci_high, 6.65, 0.01)

print()
print(analysis.conclusion())