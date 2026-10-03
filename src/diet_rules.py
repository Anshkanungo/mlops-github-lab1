"""Diet rules v1 for Pantry Path: is a grocery product vegan, vegetarian, or non-vegetarian?

`evidence` has the same shape Pantry Path's planner uses (from Open Food Facts):
    {'allergens': [...], 'traces': [...], 'complete': bool, 'ingredients_text': str}

Allergen tags are often missing (e.g. tuna with no 'fish' tag), so we check both
the tags and keywords in the ingredients text. Unknown is never guessed as safe.
"""
import re

DIETS = ('vegan', 'vegetarian', 'non-vegetarian')

# Allergen tags that reveal an animal source
MEAT_TAGS = {'fish', 'crustaceans', 'molluscs', 'gelatin', 'beef', 'pork', 'chicken'}
ANIMAL_PRODUCT_TAGS = {'milk', 'eggs', 'honey'}

# Ingredient words (singular; plurals are matched too)
MEAT_WORDS = ['meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'bacon', 'ham', 'sausage', 'lard', 'tallow',
              'gelatin', 'gelatine', 'fish', 'tuna', 'salmon', 'swordfish', 'anchovy', 'anchovies', 'sardine',
              'shrimp', 'prawn', 'crab', 'lobster', 'shellfish', 'oyster', 'animal rennet', 'carmine']
ANIMAL_PRODUCT_WORDS = ['milk', 'cream', 'butter', 'cheese', 'whey', 'casein', 'lactose', 'yogurt', 'ghee',
                        'egg', 'honey']

# Plant phrases that contain an animal word ("peanut butter", "oat milk") and must not count
PLANT_PHRASES = ['peanut butter', 'nut butter', 'almond butter', 'cocoa butter', 'shea butter',
                 'oat milk', 'oatmilk', 'soy milk', 'almond milk', 'coconut milk', 'rice milk', 'coconut cream']


def find_words(text, words):
    """Return the words from `words` that appear in `text` as whole words (plural 's' allowed)."""
    text = text.lower()
    for phrase in PLANT_PHRASES:
        text = text.replace(phrase, ' ')
    return [w for w in words if re.search(r'\b' + re.escape(w) + r's?\b', text)]


def unique(names):
    """Drop repeats, treating singular and plural as the same ('eggs' tag + 'egg' word -> 'eggs')."""
    seen, out = set(), []
    for name in names:
        if name.rstrip('s') not in seen:
            seen.add(name.rstrip('s'))
            out.append(name)
    return out


def classify(evidence):
    """Classify a product. Returns (diet, reason), where diet is one of DIETS or 'unknown'."""
    if not evidence.get('complete') or not evidence.get('ingredients_text', '').strip():
        return 'unknown', 'Incomplete ingredient evidence'
    tags = set(evidence.get('allergens', []))
    text = evidence['ingredients_text']

    meat = sorted(tags & MEAT_TAGS) + find_words(text, MEAT_WORDS)
    if meat:
        return 'non-vegetarian', 'Contains ' + ', '.join(unique(meat))
    animal = sorted(tags & ANIMAL_PRODUCT_TAGS) + find_words(text, ANIMAL_PRODUCT_WORDS)
    if animal:
        return 'vegetarian', 'Contains ' + ', '.join(unique(animal))

    # Traces ("may contain") are cross-contact, not ingredients: still vegan, but say so
    trace_animal = sorted(set(evidence.get('traces', [])) & (MEAT_TAGS | ANIMAL_PRODUCT_TAGS))
    if trace_animal:
        return 'vegan', 'No animal ingredients; may contain traces of ' + ', '.join(trace_animal)
    return 'vegan', 'No animal ingredients found'


def fits_diet(diet, evidence):
    """Can a user on `diet` eat this product? Returns (allowed, reason)."""
    if diet not in DIETS:
        return False, f'Cannot assess diet: {diet}'
    if diet == 'non-vegetarian':
        return True, 'No diet restriction'
    product_diet, reason = classify(evidence)
    if product_diet == 'unknown':
        return False, 'Withheld: ' + reason
    allowed = product_diet == 'vegan' or (diet == 'vegetarian' and product_diet == 'vegetarian')
    return allowed, reason
