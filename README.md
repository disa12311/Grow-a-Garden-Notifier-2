# Grow A Garden Discord Bot (ntfy.sh based notifications)

This is a Python-based Discord bot designed to monitor stock updates from specific Grow A Garden Discord channels and send real-time notifications via [ntfy.sh](https://ntfy.sh). The bot colorizes terminal output based on item rarity and alerts users only when tracked items appear.

---

## 📦 Features

- ✅ Tracks specific channels (e.g., stock, egg, honey, weather).
- ✅ Identifies priority items and sends notifications.
- ✅ Colored console output for easy visual tracking.
- ✅ Lightweight, no database required.
- ✅ Uses [ntfy.sh](https://ntfy.sh) for push notifications.

---

## 🛠 Requirements

- Python 3.8+
- Required packages:

```pip install discord.py requests```

---

## ⚙️ Setup Instructions

1. Clone the Repository

```
$ git clone https://github.com/yourusername/grow-a-garden-bot.git
$ cd grow-a-garden-bot
```

2. Install Dependencies

```$ pip install discord.py requests```

3. Configure the Bot

Edit the config.py file:

```
DISCORD_TOKEN = "your_discord_bot_token"

CHANNEL_IDS = {
    channelid1: "Stock",
    channelid2: "Weather",
    channelid3: "Egg Stock",
    channelid4: "Honey Stock"
}

NTFY_TOPIC = "your-ntfy-topic-name"
```

##### Replace "your_discord_bot_token" with your bot's token.

##### Replace channel IDs.

##### Replace your-ntfy-topic-name with your topic on ntfy.sh.

> Optional: You can use .env instead of config.py for security.

---

## 🚀 Run the Bot

```python main.py```

---

## 🔔 How Notifications Work

Items in default_priority_items or high_priority_items will trigger a notification.

Notifications are sent to your ntfy.sh topic.

High-priority items will use a higher notification level.

---

## 🤝 Credits

Built by Jim

[For Grow A Garden stock monitoring and alerting.]

[If you want GaG notifications without doing all this, use 'gag2-jim' as the topic name.]
