import os
import requests
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = "1188421559"

EPIC_API_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=en-US&country=BD&allowCountries=BD"
)
SEEN_FILE = "seen_games.json"


def load_seen_games():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_games(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def get_free_games():
    try:
        resp = requests.get(EPIC_API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        elements = data["data"]["Catalog"]["searchStore"]["elements"]
        free_games = []
        for game in elements:
            promotions = game.get("promotions") or {}
            offers = promotions.get("promotionalOffers", [])
            if not offers:
                continue
            for offer_group in offers:
                for offer in offer_group.get("promotionalOffers", []):
                    disc = offer.get("discountSetting", {})
                    if disc.get("discountPercentage") == 0:
                        title = game.get("title", "Unknown Game")
                        desc  = (game.get("description", "") or "")[:200]
                        slug  = game.get("productSlug") or game.get("urlSlug") or ""
                        url   = (
                            f"https://store.epicgames.com/en-US/p/{slug}"
                            if slug else
                            "https://store.epicgames.com/en-US/free-games"
                        )
                        price_info = game.get("price", {}).get("totalPrice", {})
                        original   = price_info.get("fmtPrice", {}).get("originalPrice", "")
                        free_games.append({
                            "title": title,
                            "desc": desc,
                            "url": url,
                            "original_price": original,
                            "end_date": offer.get("endDate", "")[:10],
                        })
        return free_games
    except Exception as e:
        print(f"Error fetching Epic games: {e}")
        return []


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("Telegram message sent!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def check_and_notify():
    print("Checking Epic Games free games...")
    games = get_free_games()
    seen  = load_seen_games()
    new   = [g for g in games if g["title"] not in seen]

    if not new:
        print("No new free games found.")
        return

    for game in new:
        price_text = f" (normally {game['original_price']})" if game["original_price"] else ""
        until_text = f"\n🗓 Free until: {game['end_date']}" if game["end_date"] else ""
        msg = (
            f"🎮 <b>New FREE Game on Epic!</b>\n\n"
            f"🕹 <b>{game['title']}</b>{price_text}"
            f"{until_text}\n\n"
            f"📖 {game['desc']}...\n\n"
            f"🔗 <a href=\"{game['url']}\">Claim it here →</a>"
        )
        send_telegram(msg)
        seen.add(game["title"])

    save_seen_games(seen)


if __name__ == "__main__":
    check_and_notify()
