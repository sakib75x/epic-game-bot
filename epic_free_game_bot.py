import os
import requests
import json
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = "1188421559"
SEEN_FILE = "seen_games.json"
OFFSET_FILE = "offset.json"

EPIC_API_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=en-US&country=BD&allowCountries=BD"
)

# ─────────────────────────────────────────
#  EPIC API
# ─────────────────────────────────────────

def get_free_games():
    try:
        resp = requests.get(EPIC_API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        elements = data["data"]["Catalog"]["searchStore"]["elements"]
        free_games = []
        upcoming   = []

        for game in elements:
            promotions = game.get("promotions") or {}
            title      = game.get("title", "Unknown Game")
            desc       = (game.get("description", "") or "")[:180]
            slug       = game.get("productSlug") or game.get("urlSlug") or ""
            url        = (
                f"https://store.epicgames.com/en-US/p/{slug}"
                if slug else
                "https://store.epicgames.com/en-US/free-games"
            )
            price_info = game.get("price", {}).get("totalPrice", {})
            original   = price_info.get("fmtPrice", {}).get("originalPrice", "")

            # Current free games
            for offer_group in promotions.get("promotionalOffers", []):
                for offer in offer_group.get("promotionalOffers", []):
                    if offer.get("discountSetting", {}).get("discountPercentage") == 0:
                        free_games.append({
                            "title": title, "desc": desc, "url": url,
                            "original_price": original,
                            "end_date": offer.get("endDate", "")[:10],
                        })

            # Upcoming free games
            for offer_group in promotions.get("upcomingPromotionalOffers", []):
                for offer in offer_group.get("promotionalOffers", []):
                    if offer.get("discountSetting", {}).get("discountPercentage") == 0:
                        upcoming.append({
                            "title": title,
                            "start_date": offer.get("startDate", "")[:10],
                        })

        return free_games, upcoming
    except Exception as e:
        print(f"Error fetching Epic games: {e}")
        return [], []


# ─────────────────────────────────────────
#  TELEGRAM HELPERS
# ─────────────────────────────────────────

def tg(method, payload):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


def send_message(text, reply_markup=None):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    tg("sendMessage", payload)


def main_menu_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "🎮 Current Free Games", "callback_data": "games"},
                {"text": "⏭ Next Free Games",    "callback_data": "next"},
            ],
            [
                {"text": "🔗 Open Epic Store", "url": "https://store.epicgames.com/en-US/free-games"},
            ]
        ]
    }


def answer_callback(callback_id):
    tg("answerCallbackQuery", {"callback_query_id": callback_id})


# ─────────────────────────────────────────
#  COMMAND HANDLERS
# ─────────────────────────────────────────

def handle_games():
    free_games, _ = get_free_games()
    if not free_games:
        send_message("😕 No free games right now. Check back Thursday!", main_menu_buttons())
        return
    for game in free_games:
        price_text = f" <s>{game['original_price']}</s> → <b>FREE</b>" if game["original_price"] else " → <b>FREE</b>"
        until_text = f"\n🗓 <b>Free until:</b> {game['end_date']}" if game["end_date"] else ""
        msg = (
            f"🎮 <b>{game['title']}</b>{price_text}"
            f"{until_text}\n\n"
            f"📖 {game['desc']}...\n\n"
            f"🔗 <a href=\"{game['url']}\">Claim for FREE →</a>"
        )
        send_message(msg)
    send_message("👆 Tap a link above to claim your free game!", main_menu_buttons())


def handle_next():
    _, upcoming = get_free_games()
    if not upcoming:
        send_message(
            "📅 No upcoming games info yet.\n\nEpic usually reveals next week's games on <b>Wednesday</b>. Check back then!",
            main_menu_buttons()
        )
        return
    msg = "⏭ <b>Coming soon for FREE on Epic:</b>\n\n"
    for game in upcoming:
        msg += f"🕹 <b>{game['title']}</b>"
        if game["start_date"]:
            msg += f" — from {game['start_date']}"
        msg += "\n"
    msg += "\n⏰ Epic drops new games every <b>Thursday</b>!"
    send_message(msg, main_menu_buttons())


def handle_start():
    send_message(
        "👋 <b>Welcome to Epic Free Games Bot!</b>\n\n"
        "I'll automatically notify you every time Epic gives away free games.\n\n"
        "Use the buttons below anytime to check games manually 👇",
        main_menu_buttons()
    )


# ─────────────────────────────────────────
#  AUTO NOTIFY
# ─────────────────────────────────────────

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def auto_notify():
    free_games, _ = get_free_games()
    seen = load_seen()
    new  = [g for g in free_games if g["title"] not in seen]
    if not new:
        print("No new free games to notify.")
        return
    for game in new:
        price_text = f" <s>{game['original_price']}</s> → <b>FREE</b>" if game["original_price"] else " → <b>FREE</b>"
        until_text = f"\n🗓 <b>Free until:</b> {game['end_date']}" if game["end_date"] else ""
        msg = (
            f"🚨 <b>New FREE Game on Epic!</b>\n\n"
            f"🎮 <b>{game['title']}</b>{price_text}"
            f"{until_text}\n\n"
            f"📖 {game['desc']}...\n\n"
            f"🔗 <a href=\"{game['url']}\">Claim for FREE →</a>"
        )
        tg("sendMessage", {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "🎮 Claim Now!", "url": game["url"]},
                    {"text": "📋 All Free Games", "callback_data": "games"},
                ]]
            },
        })
        seen.add(game["title"])
    save_seen(seen)


# ─────────────────────────────────────────
#  POLLING — listen for 55 seconds
# ─────────────────────────────────────────

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE) as f:
            return json.load(f).get("offset", 0)
    return 0


def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        json.dump({"offset": offset}, f)


def poll_and_respond(duration_seconds=55):
    offset   = load_offset()
    end_time = time.time() + duration_seconds
    print(f"Polling for {duration_seconds} seconds...")

    while time.time() < end_time:
        try:
            remaining = int(end_time - time.time())
            timeout   = min(10, remaining)
            if timeout <= 0:
                break

            resp    = tg("getUpdates", {"offset": offset, "timeout": timeout})
            updates = resp.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                # Button clicks
                if "callback_query" in update:
                    cb   = update["callback_query"]
                    data = cb.get("data", "")
                    answer_callback(cb["id"])
                    if data == "games":
                        handle_games()
                    elif data == "next":
                        handle_next()

                # Text commands
                if "message" in update:
                    text = update["message"].get("text", "")
                    if text.startswith("/start"):
                        handle_start()
                    elif text.startswith("/games"):
                        handle_games()
                    elif text.startswith("/next"):
                        handle_next()

            save_offset(offset)

        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Epic Free Game Bot running...")
    auto_notify()
    poll_and_respond()
    print("✅ Done.")
