# 🧠 MultiTask Lab

A student project in mathematical statistics: **does multitasking (the number of
tabs and apps open at the same time) affect short-term memory?**

The website runs a short word-memory test, saves the answers anonymously and
calculates the statistics with the same methods as in the project report.

## How it works

1. The participant answers a few questions: the number of open tabs and apps,
   hours of sleep, caffeine and tiredness.
2. 15 words are shown for 60 seconds (the same list for everyone).
3. The participant types the words they remember. The program counts the correct
   ones automatically, so the result does not depend on self-reported answers.
4. The answers are saved in a database, and the **Results** page shows the statistics.

## Statistics

- Descriptive statistics: mean, median, minimum, maximum and standard deviation
- Histograms and a scatter plot with the regression line
- Correlation coefficient r and linear regression Y = a + b·X
- Hypothesis test H₀: ρ = 0 against H₁: ρ ≠ 0 (t-test, significance levels
  α = 0.01 / 0.05 / 0.10)
- Confidence interval for the mean number of words remembered

## Data

| Source | What it is | Rows |
|---|---|---|
| `survey` | The first survey from the report (ranges replaced by their midpoints, "N+" taken as N) | 34 |
| `site` | Answers collected through the website | growing |

The survey data are loaded with `python import_survey.py`.
Result on these data: r = 0.230, p = 0.190, so no statistically significant
relationship was found.

The two sources are analysed separately by default, because they were measured
in different ways.

## Limitations

- The number of tabs and apps is reported by the participant, not measured automatically.
- The sample is a convenience sample (students who agreed to take the test), not a random one.
- Correlation does not prove causation.
- The first survey was measured less precisely than the website data: it used
  different word lists and some answers were reported by the respondents.
- Words must be typed in the same form as in the list ("apple" is counted,
  "apples" is not). Capital letters do not matter.

## Run it on your computer

```bash
git clone https://github.com/nurtileuserikbaiuly/multitask_lab.git
cd multitask_lab
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python import_survey.py
streamlit run app.py
```

## Project structure

| File | Purpose |
|---|---|
| `app.py` | The test page |
| `pages/1_Results.py` | The results page |
| `config.py` | Settings: words, time, significance level |
| `database.py` | Working with the SQLite database |
| `logic.py` | Checking the words the participant remembered |
| `stats.py` | Calculations: correlation, regression, hypothesis test |
| `charts.py` | Charts |
| `import_survey.py` | Loading the data of the first survey |

## Authors

Serikbaiuly Nurtileu, Askarkyzy Ulpan   - Narxoz university