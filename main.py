import aiohttp
import asyncio
import logging
from datetime import datetime
from src.cache import load_cache, save_cache
from src.fetch_listings import fetch_listings
from src.rns_lookup import check_rns
from src.discord_webhook import send_discord_notification

CHECK_INTERVAL = 60

logging.basicConfig(filename="sabungan_listings.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


async def fetch_exchange_rate():
    url = f"https://exchange-rate.skymavis.com/ron"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("usd", 0.0)


def truncate_address(addr: str, front: int = 6, back: int = 3) -> str:
    return f"{addr[:front]}...{addr[-back:]}"


async def main():
    cached_token_ids = set(await load_cache())

    while True:
        current_listings = await fetch_listings()
        current_ids = {listing["tokenId"] for listing in current_listings}

        new_listings = [l for l in current_listings if l["tokenId"] not in cached_token_ids]

        for listing in new_listings:
            seller_address = listing["owner"]
            listing["seller"] = seller_address

            rate = await fetch_exchange_rate()
            amount = round(float(listing["order"]["basePrice"]) / 1e18, 3)
            usd_value = round(amount * rate, 3)

            listing["amount"] = int(amount) if amount.is_integer() else amount
            listing["usd_value"] = int(usd_value) if usd_value.is_integer() else usd_value

            rns = await check_rns(seller_address)
            listing["rns_seller"] = rns if rns else truncate_address(seller_address)

            await send_discord_notification(listing)

            log_message = (
                f"TokenID: {listing['tokenId']}, "
                f"Seller: {listing['seller']}, "
                f"Price: {listing['amount']} (~{listing['usd_value']}), "
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logging.info(log_message)

        await save_cache(list(current_ids))
        cached_token_ids = current_ids

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
