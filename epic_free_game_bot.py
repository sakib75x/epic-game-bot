import os
import requests
import json
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "1188421559" 
EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=BD&allowCountries=BD"

# --- WEB SERVER (For Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running with rich formatting!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- ENHANCED EPIC GAMES LOGIC ---
def get_epic_games_rich():
    try:
        resp = requests.get(EPIC_API_URL, timeout=15)
        data = resp.json()
        elements = data["data"]["Catalog"]["searchStore"]["elements"]
        
        current_list = []
        upcoming_list = []
        
        for game in elements:
            promos = game.get("promotions") or {}
            title = game.get("title", "Unknown Game")
            desc = (game.get("description", "") or "")[:150]
            slug = game.get("productSlug") or game.get("urlSlug") or ""
            url = f"https://store.epicgames.com/en-US/p/{slug}" if slug else "https://store.epicgames.com/en-US/free-games"
            
            # Formatting Price & Dates
            price_info = game.get("price", {}).get("totalPrice", {})
            original = price_info.get("fmtPrice", {}).get("originalPrice", "")
            
            # Check Current
            offers = promos.get("promotionalOffers", [])
            for group in offers:
                for o in group.get("promotionalOffers", []):
                    if o.get("discountSetting", {}).get("discountPercentage") == 0:
                        current_list.append({
                            "title": title, "desc": desc, "url": url, 
                            "original": original, "end": o.get("endDate", "")[:10]
                        })
            
            # Check Upcoming
            next_offers = promos.get("upcomingPromotionalOffers", [])
            for group in next_offers:
                for o in group.get("promotionalOffers", []):
                    if o.get("discountSetting", {}).get("discountPercentage") == 0:
                        upcoming_list.append({"title": title, "start": o.get("startDate", "")[:10]})
                        
        return current_list, upcoming_list
    except Exception as e:
        print(f"Error: {e}")
        return [], []

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Current Free Games", callback_data='get_games')],
        [InlineKeyboardButton("⏭ Upcoming Games", callback_data='get_next')],
        [InlineKeyboardButton("🔗 Open Epic Store", url="https://store.epicgames.com/en-US/free-games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 <b>Welcome to Epic Free Games Bot!</b>\n\nI'll show you what's free right now with all the details.", 
        reply_markup=reply_markup, 
        parse_mode='HTML'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    current, upcoming = get_epic_games_rich()
    
    if query.data == 'get_games':
        if not current:
            await query.edit_message_text("No free games found right now.")
            return
        
        # We send current games as fresh messages to keep the "Rich" look with links
        for game in current:
            price_text = f"<s>{game['original']}</s> → <b>FREE</b>" if game['original'] else "<b>FREE</b>"
            msg = (
                f"🎮 <b>{game['title']}</b> {price_text}\n"
                f"🗓 Free until: {game['end']}\n\n"
                f"📖 {game['desc']}...\n\n"
                f"🔗 <a href='{game['url']}'>Claim for FREE →</a>"
            )
            await context.bot.send_message(chat_id=query.message.chat_id, text=msg, parse_mode='HTML')
            
    elif query.data == 'get_next':
        text = "⏭ <b>Upcoming Free Games:</b>\n\n"
        text += "\n".join([f"• {g['title']} (Starts: {g['start']})" for g in upcoming]) if upcoming else "No info yet."
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode='HTML')

# --- MAIN RUNNER ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()
