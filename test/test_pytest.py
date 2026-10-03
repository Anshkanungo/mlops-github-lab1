import json
from pathlib import Path

import pytest
from src import diet_rules

SNAPSHOT = Path(__file__).resolve().parent.parent / 'data' / 'products_snapshot.json'
PRODUCTS = json.loads(SNAPSHOT.read_text())['products']


def evidence(text, allergens=(), traces=(), complete=True):
    return dict(ingredients_text=text, allergens=list(allergens), traces=list(traces), complete=complete)


# 1. Every real Open Food Facts product gets the diet we read from its label
@pytest.mark.parametrize('product', PRODUCTS, ids=[p['name'] for p in PRODUCTS])
def test_classify_real_products(product):
    diet, reason = diet_rules.classify(product['evidence'])
    assert diet == product['expected_diet'], reason


# 2. Which users can eat which product
@pytest.mark.parametrize('user_diet, product_text, allowed', [
    ('vegan', 'water, organic soybeans', True),               # vegan eats tofu
    ('vegan', "pasteurized cow's milk, salt", False),         # vegan skips brie
    ('vegetarian', 'eggs', True),                             # vegetarian eats eggs
    ('vegetarian', 'swordfish', False),                       # vegetarian skips fish
    ('non-vegetarian', 'swordfish', True),                    # no restriction
])
def test_fits_diet(user_diet, product_text, allowed):
    assert diet_rules.fits_diet(user_diet, evidence(product_text))[0] is allowed


def test_incomplete_evidence_is_withheld():
    allowed, reason = diet_rules.fits_diet('vegan', evidence('water, sugar', complete=False))
    assert not allowed
    assert reason.startswith('Withheld')


def test_non_vegetarian_user_accepts_even_unknown_products():
    assert diet_rules.fits_diet('non-vegetarian', evidence('', complete=False))[0]


def test_unknown_diet_cannot_be_assessed():
    allowed, reason = diet_rules.fits_diet('keto', evidence('water'))
    assert not allowed
    assert reason == 'Cannot assess diet: keto'


# 3. Traps: words that look animal but are not, and missing tags
@pytest.mark.parametrize('text', ['peanut butter, salt', 'oat milk, sugar', 'cocoa butter, sugar', 'eggplant, olive oil'])
def test_plant_phrases_are_vegan(text):
    assert diet_rules.classify(evidence(text))[0] == 'vegan'


def test_text_catches_meat_when_tags_are_missing():
    assert diet_rules.classify(evidence('Albacore Tuna, Water, Sea Salt'))[0] == 'non-vegetarian'


def test_trace_only_stays_vegan_with_note():
    diet, reason = diet_rules.classify(evidence('durum wheat semolina', traces=['eggs']))
    assert diet == 'vegan'
    assert 'may contain traces of eggs' in reason


def test_reason_does_not_repeat_singular_and_plural():
    assert diet_rules.classify(evidence('Eggs', allergens=['eggs']))[1] == 'Contains eggs'
