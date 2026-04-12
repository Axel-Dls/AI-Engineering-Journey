import requests

def resolve_game_candidates(search_txt: str):
    if search_txt == '':
        raise ValueError("Ne peux pas rien chercher.")

    try:
        return int(search_txt)
    except ValueError:
        url = f"https://store.steampowered.com/api/storesearch/?term={search_txt}&l=english&cc=US"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        items = data["items"]

        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]
        else:
            return items

def select_game(game):
    return game