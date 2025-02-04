import aiohttp


async def fetch_listings():
    url = "https://marketplace-graphql.skymavis.com/graphql"
    query = """
    query GetListings($tokenAddress: String, $auctionType: AuctionType, $from: Int!, $size: Int!, $sort: SortBy, $rangeCriteria: [RangeSearchCriteria!]) {
        erc721Tokens(tokenAddress: $tokenAddress, auctionType: $auctionType, from: $from, size: $size, sort: $sort, rangeCriteria: $rangeCriteria) {
            total
            results {
                tokenId
                owner
                cdnImage
                attributes
                order {
                    basePrice
                    expiredAt
                }
            }
        }
    }
    """
    token_address = "0xee9436518030616bc315665678738a4348463df4"
    auction_type = "Sale"
    sort_order = "PriceAsc"
    range_criteria = []

    size = 50
    offset = 0
    all_results = []

    async with aiohttp.ClientSession() as session:
        while True:
            variables = {
                "from": offset,
                "auctionType": auction_type,
                "size": size,
                "sort": sort_order,
                "rangeCriteria": range_criteria,
                "tokenAddress": token_address
            }

            payload = {
                "operationName": "GetListings",
                "query": query,
                "variables": variables
            }

            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    tokens_data = data["data"]["erc721Tokens"]
                    total = tokens_data.get("total", 0)
                    results = tokens_data.get("results", [])
                    all_results.extend(results)

                    offset += size
                    if offset >= total:
                        break
                else:
                    break

    return all_results
