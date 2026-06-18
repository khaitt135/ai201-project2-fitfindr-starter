from tools import (
    search_listings,
    suggest_outfit,
    create_fit_card,
)

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

fit_card = create_fit_card(
    outfit,
    results[0]
)

print(fit_card)