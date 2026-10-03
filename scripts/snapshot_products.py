"""One-off: fetch real products from Open Food Facts and save them as test data.

Run once by hand (python scripts/snapshot_products.py). Tests and CI only read
the saved data/products_snapshot.json and never call the network.
"""
import json
import time
import urllib.request
from datetime import date
from pathlib import Path

API = 'https://world.openfoodfacts.org/api/v2/product/{}?fields=code,product_name,brands,ingredients_text,ingredients_text_en,allergens_tags,traces_tags,states_tags'
HEADERS = {'User-Agent': 'PantryPathLab/0.1 (student project)'}
OUT = Path(__file__).resolve().parent.parent / 'data' / 'products_snapshot.json'

# barcode -> the diet we expect from the real label (checked by hand)
PRODUCTS = {
    '0190646640026': 'vegan',           # Oatly Oat Milk
    '0016000107106': 'vegan',           # Gold Medal All Purpose Flour
    '0041390001055': 'vegan',           # Kikkoman Soy Sauce
    '0025484000124': 'vegan',           # Nasoya Organic Tofu Extra Firm
    '0076808280739': 'vegan',           # Barilla Penne ("may contain eggs" trace only)
    '0096619173969': 'vegetarian',      # Kirkland French Brie (microbial rennet)
    '0096619032938': 'vegetarian',      # Kirkland Raw Honey
    '0078742127071': 'vegetarian',      # Great Value Large White Eggs
    '0029714170106': 'non-vegetarian',  # Orca Bay Swordfish
    '0042238302211': 'non-vegetarian',  # Haribo Goldbears (gelatin)
    '0039000086639': 'non-vegetarian',  # Libby's Vienna Sausage
    '0096619977819': 'non-vegetarian',  # Kirkland Albacore Tuna (no allergen tags)
}


def fetch(barcode):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(API.format(barcode), headers=HEADERS), timeout=30) as r:
                return json.load(r)['product']
        except Exception as e:
            print(f'{barcode}: attempt {attempt + 1} failed ({e})')
            time.sleep(10)
    raise SystemExit(f'Could not fetch {barcode}')


def to_record(p, expected):
    return dict(
        barcode=p['code'],
        name=p.get('product_name', ''),
        brand=p.get('brands', ''),
        expected_diet=expected,
        evidence=dict(
            ingredients_text=p.get('ingredients_text_en') or p.get('ingredients_text', ''),
            allergens=[t.removeprefix('en:') for t in p.get('allergens_tags', [])],
            traces=[t.removeprefix('en:') for t in p.get('traces_tags', [])],
            complete='en:ingredients-completed' in p.get('states_tags', []),
        ),
    )


if __name__ == '__main__':
    records = []
    for barcode, expected in PRODUCTS.items():
        records.append(to_record(fetch(barcode), expected))
        print(f'{barcode}: {records[-1]["name"]}')
        time.sleep(1)
    OUT.write_text(json.dumps(dict(source='Open Food Facts', retrieved=date.today().isoformat(), products=records), indent=2) + '\n')
    print(f'Saved {len(records)} products to {OUT}')
