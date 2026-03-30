import os
import json
import requests
import asyncio
import threading
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- LOGGING SETUP ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
DB_FILE = "seen_games.json"

app = Flask(__name__)

# --- PERSISTENCE HELPERS ---
def load_seen_games():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_games(seen_set):
    with open(DB_FILE, 'w') as f:
        json.dump(list(seen_set), f)

# --- FLASK SERVER ---
@app.route('/')
def home():
    return "BOT_STATUS: ACTIVE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- EPIC GAMES LOGIC ---
def get_free_games():
    try:
        response = requests.get(EPIC_API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        elements = data['data']['Catalog']['searchStore']['elements']
        
        current, upcoming = [], []
        for game in elements:
            promos = game.get('promotions')
            if not promos: continue
            
            # Extract Slug for the URL
            slug = game.get('productSlug') or (game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug'))
            game['url_slug'] = slug

            if promos.get('promotionalOffers') and promos['promotionalOffers'][0]['promotionalOffers']:
                current.append(game)
            elif promos.get('upcomingPromotionalOffers') and promos['upcomingPromotionalOffers'][0]['promotionalOffers']:
                upcoming.append(game)
                
        return current, upcoming
    except Exception as e:
        logger.error(f"API Error: {e}")
        return [], []

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Current Deals", callback_query_data='current')],
                [InlineKeyboardButton("⏳ Coming Soon", callback_query_data='upcoming')]]
    await update.message.reply_text("✨ **Epic Games Tracker**\nClick below to see active freebies:", 
                                   reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current, upcoming = get_free_games()
    
    if query.data == 'current':
        msg = "<b>🌟 Available Now:</b>\n\n"
        for g in current:
            msg += f"▪️ {g['title']}\n🔗 <a href='https://store.epicgames.com/en-US/p/{g['url_slug']}'>Claim Now</a>\n\n"
    else:
        msg = "<b>⏳ Upcoming:</b>\n\n"
        for g in upcoming:
            msg += f"▪️ {g['title']} (Starts soon)\n"
            
    await query.edit_message_text(text=msg, parse_mode='HTML')

# --- BACKGROUND CHECKER ---
async def auto_check(application: Application):
    seen_games = load_seen_games()
    while True:
        current, _ = get_free_games()
        changed = False
        for game in current:
            if game['id'] not in seen_games:
                msg = (f"🚨 <b>NEW FREE GAME!</b>\n\n"
                       f"<b>{game['title']}</b> is now FREE!\n"
                       f"🔗 <a href='https://store.epicgames.com/en-US/p/{game['url_slug']}'>Claim Here</a>")
                try:
                    await application.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                    seen_games.add(game['id'])
                    changed = True
                except Exception as e:
                    logger.error(f"Send Error: {e}")
        
        if changed:
            save_seen_games(seen_games)
        await asyncio.sleep(3600) # Check every hour

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    await application.initialize()
    await application.start()
    asyncio.create_task(auto_check(application))
    await application.updater.start_polling()
    
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
