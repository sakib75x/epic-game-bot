
# 🎮 Epic Free Games Telegram Bot (24/7 Edition)

An instant, fully automated Telegram bot that notifies you the moment Epic Games Store drops a new free game. Unlike the old version, this runs **24/7 on Render**, providing instant button responses and real-time alerts.

---

## ✨ Features

- 🚀 **Instant Response** — Buttons like `/games` and `/next` respond in under a second.
- 🚨 **Auto-Notifications** — The bot checks the store every hour and alerts you automatically when a new game is found.
- 🖼️ **Rich Formatting** — Beautiful messages with emojis, original prices (strikethrough), and direct claim links.
- ☁️ **Cloud Hosted** — Runs on Render.com's free tier, so your PC doesn't need to be on.
- 💾 **Smart Memory** — Remembers which games it has already shown you to avoid spam.

---

## 📸 Preview

```text
🎮 New FREE Game Alert!

🕹 Havendock ~~$19.99~~ → FREE
🗓 Free until: 2026-04-02

📖 Build and manage your own floating town...

🔗 Claim Now →
```

---

## 🚀 Setup Guide (Render.com)

### Step 1 — Create your Bot & Chat ID
1. Create a bot via **@BotFather** on Telegram and save the **API Token**.
2. Get your **Chat ID** (the numbers) from the `@getUpdates` URL as described in the code.

### Step 2 — Get your Chat ID

Message your new bot anything (e.g. "hi")
Open this URL in browser: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
Find "chat" → "id" in the response — that's your Chat ID
you must change your chat id in epic_free_game_bot.py in code
### Step 3 — Deploy to Render
1. Create a free account at [Render.com](https://render.com) and connect your GitHub.
2. Select **New +** → **Web Service**.
3. Use these settings:
   - **Runtime**: `Python 3`.
   - **Build Command**: `pip install -r requirements.txt`.
   - **Start Command**: `python epic_free_game_bot.py`.
4. Go to the **Environment** tab and add:
   - `BOT_TOKEN`: (Your Telegram Token from BotFather).

### Step 4 — Keep it Awake (Optional but Recommended)
Render's free tier "sleeps" after 15 minutes of inactivity. To keep the bot instant:
1. Use a service like **Cron-job.org**.
2. Point it to your Render URL (e.g., `https://your-bot-name.onrender.com`) every 10 minutes.

---

## 🛠 Troubleshooting

**Bot isn't responding?**
- Check the **Logs** tab on Render. If you see `Bot started and listening...`, the code is fine.
- Check the **Environment** tab to ensure your `BOT_TOKEN` is correct.

**First click is slow?**
- If you don't use a "ping" service, the first click after a long break might take 30-50 seconds to wake Render up. After that, it stays instant.

---

## 📄 License
MIT License — free to use, modify, and share.

---

**Would you like me to help you set up the Cron-job.org ping to make sure the bot never sleeps?**
