"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    keywords = description.lower().split()

    matches = []

    for listing in listings:

        # Price filter
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter
        if size is not None:
            listing_size = listing["size"].lower()
            if size.lower() not in listing_size:
                continue

        searchable_text = " ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"])
        ]).lower()

        score = 0

        for keyword in keywords:
            if keyword in searchable_text:
                score += 1

        if score > 0:
            matches.append((score, listing))

    matches.sort(key=lambda x: x[0], reverse=True)

    return [listing for score, listing in matches]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:

    client = _get_groq_client()

    title = new_item.get("title", "item")
    description = new_item.get("description", "")

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:

        prompt = f"""
You are a fashion stylist.

Item:
{title}

Description:
{description}

The user has no wardrobe items available.

Provide:
- 2 outfit ideas
- styling advice
- overall vibe

Keep response under 150 words.
"""

    else:

        wardrobe_text = "\n".join(
            [
                f"- {item.get('name', item.get('category', 'item'))}"
                for item in wardrobe_items
            ]
        )

        prompt = f"""
You are a fashion stylist.

New item:
{title}

Description:
{description}

Wardrobe:
{wardrobe_text}

Create 1-2 complete outfits using the new item and pieces from the wardrobe.

Explain:
- what to wear together
- footwear suggestions
- overall vibe

Keep response under 150 words.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:

    if not outfit or not outfit.strip():
        return (
            "Unable to create a fit card because outfit "
            "information is missing."
        )

    client = _get_groq_client()

    title = new_item.get("title", "item")
    price = new_item.get("price", "unknown")
    platform = new_item.get("platform", "marketplace")

    prompt = f"""
Create a casual social-media outfit caption.

Item:
{title}

Price:
${price}

Platform:
{platform}

Outfit:
{outfit}

Rules:
- 2 to 4 sentences
- sound authentic
- mention item name once
- mention price once
- mention platform once
- not a product description
- feel like a real Instagram or TikTok caption
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=1.0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content.strip()