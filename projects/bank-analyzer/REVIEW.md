# Code Review — Bank Analyzer

## Table of Contents
1. [Bugs & Correctness Issues](#1-bugs--correctness-issues)
2. [Performance & Optimization](#2-performance--optimization)
3. [Missing Good Practices](#3-missing-good-practices)

---

## 1. Bugs & Correctness Issues

### ✅ 1.1 Broken column validation — `analyzer.py:53`

**Fixed.** Replaced `.isin().all()` with `required.issubset(df.columns)` so extra columns are tolerated and all required columns must be present.

---

### ✅ 1.2 Dead validation code — `analyzer.py:56–58`

**Fixed.** Removed the unreachable `is_numeric_dtype` guard. `pd.to_numeric(..., errors='raise')` already raises on failure.

---

### ✅ 1.3 Division by zero in savings rate — `analyzer.py:102`

**Fixed.** Savings rate uses a conditional expression: `... if income != 0 else 0.0`.

---

### ✅ 1.4 Fragile LLM response parsing — `analyzer.py:140`

**Fixed.** Replaced string splitting with a regex (`r'^(\d+)\.\s+(.+)'`) and a dict keyed by line number. Missing lines default to `"Autre"`.

---

### ✅ 1.5 Tests import a non-existent function — `tests/test_analyzer.py:6`

**Fixed.** Import now uses `validate_and_clean_transactions` (the real function name). `clean_transactions` removed.

---

### ✅ 1.6 `plt` global state used alongside `ax` parameter — `analyzer.py:89–91`

**Fixed.** All three calls replaced with `ax.set_title()`, `ax.tick_params()`, and `ax.figure.tight_layout()`.

---

### ✅ 1.7 `parse_qif` doesn't handle missing accounts or transactions — `file_parser.py:32–34`

**Fixed.** Guards added: raises `ValueError` if `qif.accounts` or `acc.transactions` is empty.

---

### ✅ 1.8 `train_model.py` uses a bare import — `src/train_model.py:2`

**Fixed.** Added `sys.path.insert(0, str(Path(__file__).parent.parent))` so the script can be run from the project root with `python src/train_model.py`. Import updated to `from src.analyzer import ...`.

---

### ✅ 1.9 `test_ofx.py` is a stray debug script — `test_ofx.py`

**Fixed.** File deleted.

---

## 2. Performance & Optimization

### ✅ 2.1 `get_stats(df)` computed twice on every render — `app.py:53, 88`

**Fixed.** Result stored in `stats` variable and reused.

---

### ✅ 2.2 Model loaded on every Streamlit rerun — `app.py:44`

**Fixed.** Model loading wrapped in `@st.cache_resource`.

---

### ✅ 2.3 `genai.Client` instantiated on every LLM call — `analyzer.py:118`

**Fixed.** Client created once at module level as `_gemini_client`.

---

### ✅ 2.4 `get_financial_summary` called separately in app and PDF — `app.py:57`, `pdf_report.py:24`

**Fixed.** `summary` computed once in `app.py` and passed to `generate_pdf_report`. `pdf_report.py` no longer calls `get_financial_summary`. The first chart in the PDF now reuses the already-computed `stats` variable instead of calling `get_stats(df)` twice.

---

### ✅ 2.5 List built with `.append` in a loop — `file_parser.py:19–21`, `34–35`

**Fixed.** Replaced with list comprehensions in both `parse_ofx` and `parse_qif`.

---

## 3. Missing Good Practices

### ✅ 3.1 No dependency file

**Fixed.** `pyproject.toml` added with all dependencies listed.

---

### ✅ 3.2 `src/` is not a package — missing `__init__.py`

**Fixed.** `src/__init__.py` added.

---

### ✅ 3.3 `.env` file should not be tracked by git

**Fixed.** `.env` added to `.gitignore`.

---

### ✅ 3.4 `__pycache__` directories are tracked by git

**Fixed.** `__pycache__/` and `*.pyc` added to `.gitignore`.

---

### ✅ 3.5 `model.joblib` committed to git

**Fixed.** `*.joblib` added to `.gitignore`.

---

### ✅ 3.6 No error logging — silent failure in LLM call

**Fixed.** Exception caught as `e` and logged with `logger.warning("LLM categorization failed: %s", e)`.

---

### ✅ 3.7 `load_dotenv()` called inside a business-logic function

**Fixed.** `load_dotenv()` moved to module level in both `analyzer.py` and `app.py`.

---

### ✅ 3.8 Tests only cover the happy path superficially

**Fixed.** Value assertions added: `income`, `expenses`, and `savings_rate` checked with `pytest.approx`.

---

### ✅ 3.9 Hardcoded locale in `app.py`

**Fixed.** `LOCALE = "fr"` constant defined at the top of `app.py` and used in the `get_month` call.

---

### ✅ 3.10 No `conftest.py` or path setup for `train_model.py` and root-level test

**Fixed.** `conftest.py` adds `src/` to `sys.path` for the test suite. `train_model.py` now adds the project root to `sys.path` explicitly so it can be run from anywhere. `pyproject.toml` is present.
