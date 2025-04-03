import asyncio
import logging
from datetime import datetime
from src.cache import load_cache, save_cache
from src.fetch_listings import fetch_listings
from src.rns_lookup import check_rns
from src.discord_webhook import send_discord_notification
from src.utils import fetch_exchange_rate

CHECK_INTERVAL = 60
MAX_RETRIES_PER_LISTING = 5

logging.basicConfig(
    filename="sabungan_listings.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def truncate_address(addr: str, front: int = 6, back: int = 3) -> str:
    return f"{addr[:front]}...{addr[-back:]}"


async def process_listing(listing, cached_token_ids):
    token_id = listing["tokenId"]
    retries = 0
    
    if token_id in cached_token_ids:
        logging.info(f"Listing {token_id} already processed, skipping")
        return False
    
    while retries < MAX_RETRIES_PER_LISTING:
        exchange_rate = await fetch_exchange_rate("RON")
        rate_success = exchange_rate > 0
        
        if not rate_success:
            retries += 1
            logging.warning(f"Got zero/invalid exchange rate for listing {token_id}. Retry {retries}/{MAX_RETRIES_PER_LISTING}")
            if retries < MAX_RETRIES_PER_LISTING:
                await asyncio.sleep(15)
                continue
            else:
                logging.error(f"Max retries reached for {token_id}. Unable to get valid exchange rate.")
                return False

        amount = round(float(listing["order"]["basePrice"]) / 1e18, 3)
        usd_value = round(amount * exchange_rate, 2)

        listing["amount"] = int(amount) if amount.is_integer() else amount
        listing["usd_value"] = int(usd_value) if usd_value.is_integer() else usd_value
        
        seller_address = listing["owner"]
        listing["seller"] = seller_address

        rns = await check_rns(seller_address)
        listing["rns_seller"] = rns if rns else truncate_address(seller_address)

        notification_sent = await send_discord_notification(listing)
        
        if not notification_sent:
            logging.error(f"Failed to send Discord notification for listing {token_id}")
            retries += 1
            if retries < MAX_RETRIES_PER_LISTING:
                await asyncio.sleep(15)
                continue
            else:
                logging.error(f"Max retries reached for {token_id}. Notification sending failed.")
                return False
        
        log_message = (
            f"TokenID: {token_id}, "
            f"Seller: {listing['rns_seller']}, "
            f"Price: {listing['amount']} RON (~${listing['usd_value']}), "
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logging.info(log_message)
        
        return True


async def main():
    cached_token_ids = set(await load_cache())
    pending_listings = []

    while True:
        try:
            current_listings = await fetch_listings()
            current_ids = {listing["tokenId"] for listing in current_listings}
            
            new_listings = [l for l in current_listings if l["tokenId"] not in cached_token_ids]
            
            if new_listings:
                logging.info(f"Processing {len(new_listings)} new listings")
                
                for listing in new_listings:
                    pending_listings.append(listing)
            
            if pending_listings:
                listing = pending_listings[0]
                
                success = await process_listing(listing, cached_token_ids)
                
                pending_listings.pop(0)
                if success:
                    cached_token_ids.add(listing["tokenId"])
                    await save_cache(list(cached_token_ids))
                
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(CHECK_INTERVAL)
                
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
