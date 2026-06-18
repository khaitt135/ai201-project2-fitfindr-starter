from tools import search_listings, suggest_outfit
from utils.data_loader import get_example_wardrobe

results = search_listings(
    "vintage graphic tee",
    size="M",
    max_price=50
)

outfit = suggest_outfit(
    results[0],
    get_example_wardrobe()
)

print(outfit)
