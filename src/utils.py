import aiohttp
import asyncio
import logging
from src.config import SM_KEY
from src.exchange_rate_cache import get_cached_rate, update_cache
from src.constants import TOKEN_MAPPING


async def get_token_info(token_address: str) -> (str, float):
    url = f"https://skynet-api.roninchain.com/ronin/explorer/v2/tokens/{token_address}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                result = data.get("result", {})
                symbol = result.get("symbol", "UNKNOWN")
                decimals = result.get("decimals", 18)
                divisor = 10 ** decimals
                return symbol, divisor
    return "UNKNOWN", 1e18


async def fetch_all_exchange_rates(max_retries=5, initial_delay=1):
    token_addresses = list(TOKEN_MAPPING.keys())
    addresses_param = ",".join(token_addresses)
    url = f"https://exchange-rate.skymavis.com/v2/prices?addresses={addresses_param}&vs_currencies=usd"
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        
                        if not result:
                            logging.warning(f"Empty result from exchange rate API on attempt {attempt+1}/{max_retries}")
                            continue
                        
                        for address, rates in result.items():
                            if address in TOKEN_MAPPING and "usd" in rates:
                                rate = rates["usd"]
                                if rate > 0:
                                    symbol = TOKEN_MAPPING[address][0]
                                    update_cache(symbol, rate)
                        
                        return result
                    else:
                        logging.warning(f"Failed to fetch exchange rates: HTTP {response.status} on attempt {attempt+1}/{max_retries}")
            
            retry_delay = initial_delay * (2 ** attempt)
            logging.info(f"Retrying exchange rates in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            
        except Exception as e:
            logging.error(f"Error fetching exchange rates on attempt {attempt+1}/{max_retries}: {str(e)}")
            retry_delay = initial_delay * (2 ** attempt)
            await asyncio.sleep(retry_delay)
    
    logging.error("All retries failed for fetching exchange rates")
    return {}


async def fetch_exchange_rate(token_symbol: str, max_retries=5, initial_delay=1) -> float:
    cached_rate = get_cached_rate(token_symbol)
    if cached_rate and cached_rate > 0:
        logging.info(f"Using cached exchange rate for {token_symbol}: {cached_rate}")
        return cached_rate
    
    token_address = None
    for addr, (symbol, _) in TOKEN_MAPPING.items():
        if symbol == token_symbol:
            token_address = addr
            break
    
    if not token_address:
        logging.error(f"No address mapping found for token symbol: {token_symbol}")
        return 0.0
    
    rates = await fetch_all_exchange_rates(max_retries, initial_delay)
    if token_address in rates and "usd" in rates[token_address]:
        rate = rates[token_address]["usd"]
        if rate > 0:
            update_cache(token_symbol, rate)
            return rate
    
    if cached_rate is not None:
        logging.warning(f"Using last known cached rate for {token_symbol} after all retries failed")
        return cached_rate
    
    logging.error(f"Failed to get exchange rate for {token_symbol} and no cache available")
    return 0.0
