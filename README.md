# QA Job Crawler

A professional, asynchronous Python crawler for collecting QA Engineer job listings from CakeResume, with automated posting to Discord channels. Supports both Discord Webhook and Bot (with auto-delete feature). Designed for reliability, extensibility, and team collaboration.

---

## 🚀 Project Overview

This project provides a robust solution for automatically scraping QA/Test/SDET/Quality-related job postings from CakeResume (Taipei & New Taipei, full-time, entry & mid-senior level) and delivering them to Discord. It is ideal for HR, tech communities, and job seekers who want real-time, filtered job information in their Discord channels.

---

## ✨ Features

- **Targeted Scraping**: Only QA/Test/SDET/Quality jobs, filtered by keywords (Chinese & English)
- **Location & Seniority Filtering**: Taipei City, New Taipei City, full-time, entry & mid-senior level
- **Batch Discord Delivery**: Customizable jobs per message, beautiful formatting
- **Supports Webhook & Bot**: Webhook for simple push, Bot for advanced features (auto-delete after 7 days or custom seconds)
- **Configurable**: Max pages, frequency, keywords, and message format
- **Error Handling**: Robust logging and graceful error recovery
- **Easy to Extend**: Modular code, easy to add new job sources or output channels

---

## 🛠️ Architecture & Workflow

1. **Async Crawler**: Uses `aiohttp` and `pyquery` for fast, non-blocking scraping
2. **Job Filtering**: Extracts and filters jobs by title keywords and location
3. **Batching**: Groups jobs for Discord delivery (configurable batch size)
4. **Discord Integration**: Sends jobs via Webhook or Bot (with per-message auto-delete)
5. **Auto-Stop**: Stops automatically after crawling all pages or if no jobs are found

---

## 📦 Environment Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Create & Activate Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration & Parameters

All main settings are in `cake_qa_crawler.py` or `discord_bot.py`:

| Parameter             | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL (for Webhook mode)                     |
| `TOKEN`               | Discord Bot Token (for Bot mode)                           |
| `CHANNEL_ID`          | Discord Channel ID (for Bot mode)                          |
| `JOBS_PER_MESSAGE`    | Number of jobs per Discord message (default: 10)           |
| `MAX_PAGES`           | Max pages to crawl before stopping (default: 9)            |
| `REQUEST_FREQUENCY`   | Interval between requests in milliseconds (default: 10000) |
| `PARAMS`              | Filters for location, job type, seniority                  |
| `KEYWORDS`            | List of keywords for job title filtering                   |

---

## 📖 Usage

### Webhook Mode (Default)

1. Set your Discord Webhook URL in `cake_qa_crawler.py`:
   ```python
   DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/xxxx/yyyy"
   ```
2. Run the crawler:
   ```bash
   python cake_qa_crawler.py
   ```
3. Jobs will be sent to your Discord channel in batches. The script stops after all pages are crawled.

### Bot Mode (Per-message auto-delete)

1. [Create a Discord Bot and invite it to your server.](https://discord.com/developers/applications)
2. Get your Bot Token and Channel ID (see FAQ below).
3. Use the following sample code to send and auto-delete messages:

   ```python
   import discord
   import asyncio

   TOKEN = 'YOUR_BOT_TOKEN'
   CHANNEL_ID = 123456789012345678

   intents = discord.Intents.default()
   client = discord.Client(intents=intents)

   @client.event
   async def on_ready():
       channel = client.get_channel(CHANNEL_ID)
       msg = await channel.send("This is a job message!")
       asyncio.create_task(delete_later(msg, 604800))  # 7 days (or any seconds you want)
       await client.close()

   async def delete_later(msg, delay):
       await asyncio.sleep(delay)
       await msg.delete()

   client.run(TOKEN)
   ```

   **Now, each message sent by the bot will be automatically deleted after the specified time (e.g., 7 days or 20 seconds).**

#### Advantages of Per-message Auto-delete

- Every job message is deleted automatically after its own countdown (e.g., 7 days after it is sent)
- No need for batch deletion or scheduled tasks
- Keeps the channel clean and always up-to-date

#### Note

- Bot can only delete messages it sent itself (not webhook or other users' messages)
- Make sure the bot has "Manage Messages" permission in the channel

---

## ❓ FAQ

**Q: How do I get my Discord Channel ID?**  
A: Enable Developer Mode in Discord settings, right-click the channel, and select "Copy ID".

**Q: How do I get my Bot Token?**  
A: In the Discord Developer Portal, go to your application > Bot > Reset Token.

**Q: Can Webhook messages be auto-deleted?**  
A: No, only Bot messages can be deleted programmatically.

**Q: How do I change the filter keywords or location?**  
A: Edit the `KEYWORDS` list or `PARAMS` dictionary in `cake_qa_crawler.py` or `discord_bot.py`.
