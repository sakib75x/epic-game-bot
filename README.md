# 🎮 Epic Free Games Telegram Bot

A free, fully automated Telegram bot that notifies you whenever the Epic Games Store drops a new free game. It also includes interactive buttons to check current and upcoming free games instantly.

Host it for 100% free on **Render.com** (no credit card required).

---<img width="463" height="784" alt="image" src="https://github.com/user-attachments/assets/a91c0592-8227-472a-b75a-e593f38dfcca" />


## ✨ Features

- 🚨 **Auto Notifications** — Get a Telegram message the moment a new free game is available.
- 🎮 **Interactive Menu** — Check current free games with direct claim links.
- ⏭️ **Upcoming Games** — See what's coming next before it drops.
- 💸 **100% Free** — Uses Render's free tier and Cron-job.org to stay online 24/7.
- 🛠️ **Privacy Focused** — No personal IDs are stored in the code.

---

## 🚀 Setup Guide

### Step 1 — Create a Telegram Bot
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the instructions to name your bot.
3. Copy the **API Token** provided (e.g., `123456:ABC-DEF...`).

### Step 2 — Get your Telegram Chat ID
1. Open your new bot in Telegram and click **Start** or send it any message (e.g., "hi").
2. Open your browser and go to this URL (replace `<YOUR_TOKEN>` with your actual token):
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Look for the `"chat"` section and find the `"id"` number (e.g., `1188421559`).
   * *Note: If the page is empty `[]`, send another message to the bot and refresh.*

### Step 3 — Fork & Deploy
1. **Fork** this repository to your own GitHub account.
2. Create a free account at **[Render.com](https://render.com)**.
3. Click **New +** > **Web Service** and connect your forked GitHub repository.

### Step 4 — Set Environment Variables (Important!)
In your Render dashboard, go to the **Environment** tab and add these two variables:
- `BOT_TOKEN`: (Paste your token from @BotFather)
- `CHAT_ID`: (Paste your ID from Step 2)

---

## 🛠️ Keeping it Awake (24/7)
Render's free tier "sleeps" after 15 minutes of inactivity. To keep your bot responsive:
1. Create a free account at **[Cron-job.org](https://cron-job.org)**.
2. Create a new cron job pointing to your Render URL (e.g., `https://your-bot-name.onrender.com`).
3. Set it to run every **10 to 14 minutes**.

---

## 📁 File Structure
- `epic_free_game_bot.py`: The main bot logic (Python 3.14+ compatible).
- `requirements.txt`: List of necessary libraries for Render to install.
- `seen_games.json`: Automatically created to prevent duplicate notifications.

---

## 📄 License
MIT License — Feel free to use, modify, and share!

---

> ⭐ If this bot helped you, please consider giving this repository a star!
