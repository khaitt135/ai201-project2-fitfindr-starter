from tools import search_listings

results = search_listings(
    "vintage graphic tee",
    size="M",
    max_price=50
)

print(f"Found {len(results)} results")

for item in results[:3]:
    print(item["title"])
