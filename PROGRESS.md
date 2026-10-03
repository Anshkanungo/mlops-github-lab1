# Progress

**Current status:** All lab files are written and tests pass locally (pytest 34/34, unittest 7/7). Next: git init, first commit, push, and check both workflows on GitHub.

## Todo
- [ ] `git init`, set the repo-only identity (Ansh Kanungo <anshkanungo17@gmail.com>), add remote, first commit (after explicit yes)
- [ ] Push to https://github.com/Anshkanungo/mlops-github-lab1 (done by Ansh, manually)
- [ ] Check both workflows are green in the Actions tab and `test-results` artifact is present
- [ ] Submit the lab (repo link)
- [ ] Later: copy `diet_rules.py` into Pantry Path's `planner.py` (separate, needs approval)

## Done
- 2026-10-03: README with "What I changed" table, CI badges, run steps, limitations
- 2026-10-03: GitHub Actions workflows `pytest_action.yml` and `unittest_action.yml` (Python 3.12, actions @v7), YAML parsed and commands verified locally
- 2026-10-03: `requirements.txt` (pytest) and `.gitignore`
- 2026-10-03: `test/test_pytest.py` (27 tests) and `test/test_unittest.py` (7 tests); a deliberately broken rule made 2 tests fail, as expected
- 2026-10-03: `src/diet_rules.py` (`classify`, `fits_diet`); 12/12 real products classified correctly
- 2026-10-03: Fetched 12 real Open Food Facts products into `data/products_snapshot.json` via `scripts/snapshot_products.py`
- 2026-10-03: Created folders and `.venv` (Python 3.14, pytest 9.1.1)

## Decisions
- Lab choice: GitHub Labs Lab1, because its output (diet rules + tests + CI) is real Pantry Path work. FastAPI/Nutri-Score was dropped: Pantry Path trains no model.
- Scope: only vegan / vegetarian / non-vegetarian. Celiac, pregnancy, halal, kosher come later.
- Data: Open Food Facts API, fetched once and saved, so tests and CI never call the network. Kaggle was considered and skipped (large manual download, 2017 data).
- Rules read both allergen tags and ingredients text, since tags are often missing (tuna, honey).
- "May contain" traces don't change a product's diet; the reason mentions them.
- Incomplete evidence → `unknown` → withheld for vegan/vegetarian users; never guessed.
- Workflows modernized (Python 3.12, @v7 actions) and the original YAML bugs fixed.

## Open questions
- None right now.
