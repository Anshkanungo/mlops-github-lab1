import json
import os
import sys
import unittest
from pathlib import Path

# Get the path to the project's root directory (same as the original lab)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src import diet_rules

SNAPSHOT = Path(project_root) / 'data' / 'products_snapshot.json'


def evidence(text, allergens=(), traces=(), complete=True):
    return dict(ingredients_text=text, allergens=list(allergens), traces=list(traces), complete=complete)


class TestClassify(unittest.TestCase):

    def test_real_products(self):
        for product in json.loads(SNAPSHOT.read_text())['products']:
            with self.subTest(product=product['name']):
                diet, reason = diet_rules.classify(product['evidence'])
                self.assertEqual(diet, product['expected_diet'], reason)

    def test_plant_phrases_are_vegan(self):
        for text in ['peanut butter, salt', 'oat milk, sugar', 'cocoa butter, sugar', 'eggplant, olive oil']:
            with self.subTest(text=text):
                self.assertEqual(diet_rules.classify(evidence(text))[0], 'vegan')

    def test_text_catches_meat_when_tags_are_missing(self):
        self.assertEqual(diet_rules.classify(evidence('Albacore Tuna, Water, Sea Salt'))[0], 'non-vegetarian')

    def test_trace_only_stays_vegan_with_note(self):
        diet, reason = diet_rules.classify(evidence('durum wheat semolina', traces=['eggs']))
        self.assertEqual(diet, 'vegan')
        self.assertIn('may contain traces of eggs', reason)


class TestFitsDiet(unittest.TestCase):

    def test_who_can_eat_what(self):
        cases = [
            ('vegan', 'water, organic soybeans', True),
            ('vegan', "pasteurized cow's milk, salt", False),
            ('vegetarian', 'eggs', True),
            ('vegetarian', 'swordfish', False),
            ('non-vegetarian', 'swordfish', True),
        ]
        for user_diet, text, allowed in cases:
            with self.subTest(user_diet=user_diet, text=text):
                self.assertEqual(diet_rules.fits_diet(user_diet, evidence(text))[0], allowed)

    def test_incomplete_evidence_is_withheld(self):
        allowed, reason = diet_rules.fits_diet('vegan', evidence('water, sugar', complete=False))
        self.assertFalse(allowed)
        self.assertTrue(reason.startswith('Withheld'))

    def test_unknown_diet_cannot_be_assessed(self):
        self.assertEqual(diet_rules.fits_diet('keto', evidence('water')), (False, 'Cannot assess diet: keto'))


if __name__ == '__main__':
    unittest.main()
