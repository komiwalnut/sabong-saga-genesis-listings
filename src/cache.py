import json
import os

CACHE_DIR = "data"
CACHE_FILE = os.path.join(CACHE_DIR, "listings_cache.json")

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w") as f:
        json.dump([], f)


async def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []


async def save_cache(token_ids):
    with open(CACHE_FILE, "w") as f:
        json.dump(token_ids, f, indent=4)
