import aiohttp
import logging
from datetime import datetime, timezone
from src.config import DISCORD_WEBHOOK_URL


async def send_discord_notification(listing):
    token_id = listing["tokenId"]
    cdn_image = listing["cdnImage"]

    amount = listing["amount"]
    usd_value = listing["usd_value"]

    amount_str = str(float(amount)).rstrip('0').rstrip('.')
    usd_str = str(float(usd_value)).rstrip('0').rstrip('.')
    
    payment_info = f"{amount_str} RON (~${usd_str})"

    embed = {
        "author": {
            "name": "Sabong Saga Genesis",
            "icon_url": "https://cdn.skymavis.com/ronin/2020/erc721/0xee9436518030616bc315665678738a4348463df4/logo.png"
        },
        "title": f"Chicken #{token_id}",
        "url": f"https://marketplace.skymavis.com/collections/sabong-saga-genesis/{token_id}",
        "color": 5763719,
        "fields": [
            {"name": "Price", "value": payment_info, "inline": True},
            {"name": "Seller", "value": f"[{listing['rns_seller']}](https://marketplace.skymavis.com/account/{listing['seller']})", "inline": True},
            {"name": "Expiration", "value": f"<t:{listing['order']['expiredAt']}:R>", "inline": True},
        ],
        "thumbnail": {"url": cdn_image},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    group1_keys = [
        "feet", "tail", "body", "wings", "eyes",
        "beak", "comb", "instinct", "color",
        "daily feathers", "legendary count"
    ]
    attributes = listing.get("attributes", {})
    for key in group1_keys:
        if key in attributes:
            field_value = ", ".join(attributes[key]).capitalize()
            embed["fields"].append({
                "name": key.title(),
                "value": field_value.title(),
                "inline": True
            })

    if "birthdate" in attributes:
        try:
            birth_epoch = int(attributes["birthdate"][0])
            birthdate_str = datetime.fromtimestamp(birth_epoch).strftime("%d %b %Y")
            embed["fields"].append({
                "name": "Birthdate",
                "value": birthdate_str,
                "inline": True
            })
        except Exception as e:
            logging.error(f"Error formatting birthdate: {str(e)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}) as response:
                success = response.status == 204
                if not success:
                    response_text = await response.text()
                    logging.error(f"Discord API error: Status {response.status}, Response: {response_text}")
                return success
    except Exception as e:
        logging.error(f"Exception when sending Discord notification: {str(e)}")
        return False
