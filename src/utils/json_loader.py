import json

def get_tarot_cards(path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
