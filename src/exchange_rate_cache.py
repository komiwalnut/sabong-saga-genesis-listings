import json
import os
import time

CACHE_DIR = "data"
EXCHANGE_RATE_CACHE_FILE = os.path.join(CACHE_DIR, "exchange_rate_cache.json")
CACHE_EXPIRY = 60

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

if not os.path.exists(EXCHANGE_RATE_CACHE_FILE):
    with open(EXCHANGE_RATE_CACHE_FILE, "w") as f:
        json.dump({}, f)


def load_exchange_rate_cache():
    try:
        with open(EXCHANGE_RATE_CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_exchange_rate_cache(cache):
    with open(EXCHANGE_RATE_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)


def get_cached_rate(token_symbol="RON"):
    cache = load_exchange_rate_cache()
    token_data = cache.get(token_symbol.lower(), {})
    
    if not token_data:
        return None
    
    timestamp = token_data.get("timestamp", 0)
    if time.time() - timestamp > CACHE_EXPIRY:
        return None
    
    return token_data.get("rate")


def update_cache(token_symbol, rate):
    cache = load_exchange_rate_cache()
    cache[token_symbol.lower()] = {
        "rate": rate,
        "timestamp": time.time()
    }
    save_exchange_rate_cache(cache)
