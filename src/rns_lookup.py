import aiohttp
from eth_utils import keccak
import string
from src.config import SM_KEY


def name_hash(name: str) -> str:
    node = b'\x00' * 32
    if name:
        labels = name.split(".")
        for label in reversed(labels):
            node = keccak(node + keccak(label.encode('utf-8')))
    return '0x' + node.hex()


def clean_hex_to_string(hex_str: str) -> str:
    hex_str = hex_str[2:] if hex_str.startswith('0x') else hex_str
    byte_data = bytes.fromhex(hex_str)
    decoded_str = byte_data.decode('utf-8', errors='ignore')
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, decoded_str)).strip()


async def check_rns(owner_address: str) -> str:
    reverse_domain = owner_address[2:] + ".addr.reverse"
    reverse_name_hash = name_hash(reverse_domain)

    url = 'https://api-gateway.skymavis.com/rpc/'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': SM_KEY
    }
    payload = {
        "method": "eth_call",
        "params": [
            {
                "to": "0xadb077d236d9e81fb24b96ae9cb8089ab9942d48",
                "data": f"0x691f3431{reverse_name_hash[2:]}"
            },
            "latest"
        ],
        "id": 0,
        "jsonrpc": "2.0"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response_data = await response.json()
            hex_result = response_data.get('result', '')
            rns_name = clean_hex_to_string(hex_result)
        return rns_name
