from typing import Any

def normalize_history_data(data: dict) -> dict:
    cards = data.get("cards")
    if isinstance(cards, list):
        data["cards"] = {
            "cards": cards,
            "reversed": [False] * len(cards)
        }
    return data