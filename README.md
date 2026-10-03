# GitHub Lab 1: Diet Rules for Pantry Path

[![Testing with Pytest](https://github.com/Anshkanungo/mlops-github-lab1/actions/workflows/pytest_action.yml/badge.svg)](https://github.com/Anshkanungo/mlops-github-lab1/actions/workflows/pytest_action.yml)
[![Python Unittests](https://github.com/Anshkanungo/mlops-github-lab1/actions/workflows/unittest_action.yml/badge.svg)](https://github.com/Anshkanungo/mlops-github-lab1/actions/workflows/unittest_action.yml)

A modified version of [GitHub Labs / Lab1](https://github.com/raminmohammadi/MLOps/tree/main/Labs/Github_Labs/Lab1) from the MLOps course (IE 7374, Northeastern University). The original lab tests a small `calculator.py`. This version tests **diet rules v1** for **Pantry Path**, our grocery-planning project: given a real grocery product, is it vegan, vegetarian, or non-vegetarian, and can a given user eat it?

## Scenario
In Pantry Path, an LLM turns a dish ("I want quiche") into a shopping list, and a store search finds a product for each ingredient. This lab covers the **next step**: checking each product against the user's diet. It does not include the chat or search.

- **Input:** a product's label evidence from Open Food Facts: ingredients text, allergen tags, trace ("may contain") tags, and whether the ingredient list is complete.
- **Output:** the product's diet (`vegan`, `vegetarian`, `non-vegetarian`, or `unknown`) with a reason, and for a user's diet, whether the product is allowed.

## What I changed from the original lab
| Original lab | This version |
|---|---|
| `src/calculator.py` (add, subtract, multiply) | `src/diet_rules.py`: `classify()` and `fits_diet()` for vegan / vegetarian / non-vegetarian |
| Made-up numbers in tests | **12 real products** from Open Food Facts in `data/products_snapshot.json`, with the expected diet read from each label |
| `data/` left empty | `data/products_snapshot.json` plus `scripts/snapshot_products.py`, the one-off script that fetched it |
| 4 pytest + 4 unittest tests | 27 pytest tests (using `@pytest.mark.parametrize`) + 7 unittest tests (using `subTest`) |
| Workflows on Python 3.8 and `@v2` actions | Python 3.12 and `@v7` actions (`upload-artifact@v2` no longer works) |
| Workflow YAML bugs (`run-nam:` typo; `branches` and `branches-ignore` together) | Fixed; workflows also run on pull requests into `main` |

## How the rules work
1. **Incomplete evidence → `unknown`.** We never guess; a vegan or vegetarian user doesn't get the product.
2. **Meat, fish, or gelatin** (tags or ingredient words) → `non-vegetarian`.
3. **Milk, eggs, or honey** → `vegetarian`.
4. Otherwise → `vegan`. "May contain" traces don't change this, but the reason mentions them.

Real labels taught us two things:
- **Allergen tags are often missing.** The tuna and honey in the snapshot have no tags, so the rules also read the ingredients text.
- **Some animal words are plant-based.** "Peanut butter", "oat milk", "cocoa butter" and "eggplant" are not counted as animal products.

## Project structure
```
├── .github/workflows/
│   ├── pytest_action.yml      # runs pytest, uploads pytest-report.xml
│   └── unittest_action.yml    # runs python -m unittest test.test_unittest
├── data/products_snapshot.json
├── scripts/snapshot_products.py
├── src/diet_rules.py
├── test/test_pytest.py
├── test/test_unittest.py
└── requirements.txt
```

## Run locally
```sh
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest -v                        # 34 tests (pytest also runs the unittest file)
python -m unittest test.test_unittest -v
```
The tests read only the saved snapshot and never call the network. To refresh the data (optional): `python scripts/snapshot_products.py`.

## Data
Product data from [Open Food Facts](https://world.openfoodfacts.org) (Open Database License), retrieved 2026-10-03.

## Limitations
- The rules are keyword-based (v1). They are for a demo, not dietary or medical advice. Always check the packaging.
- Only vegan, vegetarian and non-vegetarian are covered. Allergy and special diets (celiac, pregnancy, halal, kosher) come later.
