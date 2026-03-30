# 🎮 Epic Free Games Telegram Bot

A free, fully automated Telegram bot that notifies you whenever Epic Games Store drops a new free game — and lets you check current & upcoming free games anytime with a button click.

No server needed. Runs 100% free on GitHub Actions.

---

## ✨ Features

- 🚨 **Auto notifications** — get a Telegram message the moment a new free game drops
- 🎮 `/games` — see all current free games with claim links
- ⏭ `/next` — see upcoming free games before they drop
- 🖱️ **Clickable buttons** — no need to type commands, just tap
- 💸 **Completely free** — runs on GitHub Actions, no server, no credit card
- ⚡ **Checks every 5 minutes** — buttons respond fast

---

## 📸 Preview

```
🚨 New FREE Game on Epic!

🎮 Havendock  ~~$19.99~~ → FREE
🗓 Free until: 2026-04-02

📖 Build and manage your own floating town...

🔗 Claim for FREE →
```

Buttons:
```
[ 🎮 Current Free Games ]  [ ⏭ Next Free Games ]
[        🔗 Open Epic Store        ]
```

---

## 🚀 Setup Guide

### Step 1 — Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. Copy the **API token** you receive (looks like `123456789:ABCdef...`)

### Step 2 — Get your Telegram Chat ID

1. Send any message to your new bot (e.g. "hi")
2. Open this URL in your browser (replace with your token):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Find `"chat"` → `"id"` in the response — that's your Chat ID
4. If the result is empty, try:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates?offset=-1
   ```

### Step 3 — Fork this Repository

1. Click the **Fork** button at the top right of this page
2. This creates your own copy of the bot

### Step 4 — Add your Bot Token as a Secret

1. Go to your forked repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `BOT_TOKEN`
4. Value: paste your Telegram bot token
5. Click **"Add secret"**

### Step 5 — Add your Chat ID to the bot file

1. In your repo, open `epic_free_game_bot.py`
2. Click the **pencil ✏️** icon to edit
3. Find this line near the top:
   ```python
   CHAT_ID = "YOUR_CHAT_ID"
   ```
4. Replace `YOUR_CHAT_ID` with your actual Chat ID (e.g. `"123456789"`)
5. Click **"Commit changes"**

### Step 6 — Enable GitHub Actions

1. Go to the **Actions** tab in your repo
2. If you see a warning, click **"I understand my workflows, enable them"**

### Step 7 — Test it manually

1. Go to **Actions** tab → click **"Epic Free Game Bot"** on the left
2. Click **"Run workflow"** → **"Run workflow"** (green button)
3. Wait ~30 seconds
4. Send `/start` to your Telegram bot — you should see the menu with buttons!

---

## 🔧 How it Works

```
Every 5 minutes (GitHub Actions)
         │
         ├── Check Epic Games API for new free games
         │       └── If new game found → send Telegram notification
         │
         └── Listen for 55 seconds for button clicks / commands
                 ├── /start  → show welcome message + buttons
                 ├── /games  → show current free games
                 └── /next   → show upcoming free games
```

GitHub Actions caches the state (seen games + message offset) between runs so the bot remembers which games it already notified you about.

---

## 📁 File Structure

```
epic-game-bot/
├── epic_free_game_bot.py      # Main bot code
└── .github/
    └── workflows/
        └── run_bot.yml        # GitHub Actions schedule config
```

---

## ⚙️ Configuration

All configuration is at the top of `epic_free_game_bot.py`:

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Pulled from GitHub Secrets automatically |
| `CHAT_ID` | Your Telegram Chat ID (set this manually) |
| `EPIC_API_URL` | Epic Games Store API endpoint |

To change the country/locale, edit the `EPIC_API_URL`:
```python
EPIC_API_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=en-US&country=US&allowCountries=US"  # change BD to your country code
)
```

---

## 🛠 Troubleshooting

**Bot not sending messages?**
- Check that `BOT_TOKEN` secret is set correctly in GitHub
- Make sure your `CHAT_ID` is correct in the bot file
- Go to Actions tab and check the run logs for errors

**Buttons not responding?**
- Buttons respond within 5 minutes (that's how often GitHub Actions runs)
- Check the Actions tab to make sure workflows are enabled

**Getting empty `[]` when finding Chat ID?**
- Send your bot a message first, THEN open the getUpdates URL
- Or add `?offset=-1` to the URL

**Actions tab says workflows are disabled?**
- Go to Actions tab → click "Enable workflows"

---

## 📄 License

MIT License — free to use, modify, and share.

---

## 🙏 Credits

Built with:
- [python-telegram-bot](https://core.telegram.org/bots/api) (Telegram Bot API)
- [Epic Games Store API](https://store.epicgames.com)
- [GitHub Actions](https://github.com/features/actions)

---

> ⭐ If this bot helped you grab free games, consider starring the repo!
