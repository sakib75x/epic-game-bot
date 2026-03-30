import os
import requests
import json
import time
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Note: CHAT_ID is used for the automatic Thursday notifications
CHAT_ID = "1188421559" 
EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=BD&allowCountries=BD"

# --- WEB SERVER (For Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    # Render provides a $PORT environment variable automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- EPIC GAMES LOGIC ---
def get_epic_games():
    try:
        resp = requests.get(EPIC_API_URL, timeout=15)
        data = resp.json()
        elements = data["data"]["Catalog"]["searchStore"]["elements"]
        
        current_games = []
        upcoming_games = []
        
        for game in elements:
            promos = game.get("promotions") or {}
            # Current Free Games
            offers = promos.get("promotionalOffers", [])
            for group in offers:
                for o in group.get("promotionalOffers", []):
                    if o.get("discountSetting", {}).get("discountPercentage") == 0:
                        current_games.append(game.get("title"))
            
            # Upcoming Games
            next_offers = promos.get("upcomingPromotionalOffers", [])
            for group in next_offers:
                for o in group.get("promotionalOffers", []):
                    if o.get("discountSetting", {}).get("discountPercentage") == 0:
                        upcoming_games.append(game.get("title"))
                        
        return list(set(current_games)), list(set(upcoming_games))
    except:
        return [], []

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Current Free Games", callback_data='get_games')],
        [InlineKeyboardButton("⏭ Upcoming Games", callback_data='get_next')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Click a button to see Epic Games:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    current, upcoming = get_epic_games()
    
    if query.data == 'get_games':
        text = "<b>Current Free Games:</b>\n" + ("\n".join(current) if current else "None right now.")
    else:
        text = "<b>Upcoming Free Games:</b>\n" + ("\n".join(upcoming) if upcoming else "No info yet.")
        
    await query.edit_message_text(text=text, parse_mode='HTML')

# --- MAIN BOT RUNNER ---
def main():
    # 1. Start Web Server in a background thread so Render is happy
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Start the Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot started and listening...")
    application.run_polling()

if __name__ == '__main__':
    main()
