"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""
import re
from tools import search_listings, suggest_outfit, create_fit_card

print("AGENT FILE LOADED")
# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:

    session = _new_session(query, wardrobe)

    query_lower = query.lower()

    # Extract price
    price_match = re.search(r"\$(\d+)", query)
    max_price = float(price_match.group(1)) if price_match else None

    # Extract size
    size_match = re.search(r"size\s+([A-Za-z/]+)", query_lower)
    size = size_match.group(1).upper() if size_match else None

    # Create description by removing price and size phrases
    description = query_lower
    description = re.sub(r"\$\d+", "", description)
    description = re.sub(r"size\s+[A-Za-z/]+", "", description)
    description = description.replace("under", "")
    description = description.strip()

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    results = search_listings(
        description=description,
        size=size,
        max_price=max_price,
    )

    session["search_results"] = results

    if not results:
        session["error"] = (
            "No matching listings found. Try adjusting your search criteria."
        )
        return session

    session["selected_item"] = results[0]

    outfit = suggest_outfit(
        session["selected_item"],
        wardrobe,
    )

    session["outfit_suggestion"] = outfit

    fit_card = create_fit_card(
        outfit,
        session["selected_item"],
    )

    session["fit_card"] = fit_card

    return session

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )

    print("ERROR:", session["error"])
    print("ITEM:", session["selected_item"]["title"])
    print()
    print("OUTFIT:")
    print(session["outfit_suggestion"])
    print()
    print("FIT CARD:")
    print(session["fit_card"])