# QA Job Crawler

A professional Discord Bot that automatically crawls QA Engineer job listings from CakeResume and posts them to a specified Discord channel. Features automatic message deletion to keep the channel clean.

---

## 🚀 Project Overview

This project provides an automated solution for scraping QA/Test/SDET/Quality-related job postings from CakeResume (Taipei City and New Taipei City, full-time, entry and mid-senior level positions) and delivering them to Discord. Perfect for HR, tech communities, and job seekers who want real-time, filtered job information in their Discord channels.

---

## ✨ Features

- **Targeted Scraping**: Only QA/Test/SDET/Quality jobs, filtered by Chinese and English keywords
- **Location & Seniority Filtering**: Taipei City, New Taipei City, full-time, entry and mid-senior level positions
- **Batch Delivery**: Configurable jobs per message with beautiful formatting
- **Auto-delete**: Messages are automatically deleted after 7 days to maintain channel cleanliness
- **Error Handling**: Robust logging and graceful error recovery

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

### 4. Configure Environment Variables

Create a `.env` file in the project root directory with the following content:

```
DISCORD_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_channel_id
```

The bot uses `python-dotenv` to read these values directly from the `.env` file.

---

## ⚙️ Configuration Parameters

Main settings are in `discord_bot.py`:

| Parameter          | Description                                     | Default                                                                                       |
| ------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `JOBS_PER_MESSAGE` | Number of jobs per message                      | 10                                                                                            |
| `MAX_PAGES`        | Maximum pages to crawl                          | 9                                                                                             |
| `KEYWORDS`         | Job title keywords filter                       | ['qa', '測試', 'test', 'testing', 'sdet', 'quality', '品質', 'quality assurance', '軟體測試'] |
| `PARAMS`           | Location, job type, and seniority level filters | See code                                                                                      |

---

## 📖 Usage

1. Create a Bot in Discord Developer Portal and get the Token
2. Invite the Bot to your server
3. Create and configure your `.env` file as described above
4. Run the Bot:
   ```bash
   python discord_bot.py
   ```

The bot will:

- Crawl job listings from CakeResume
- Filter jobs based on keywords and parameters
- Send formatted messages to the specified Discord channel
- Automatically delete messages after 7 days

---

## ❓ FAQ

**Q: How do I get the Discord Channel ID?**  
A: Enable Developer Mode in Discord settings, right-click the channel, and select "Copy ID".

**Q: How do I get the Bot Token?**  
A: In the Discord Developer Portal, go to your application > Bot > Reset Token.

**Q: How do I modify the filter keywords or location?**  
A: Edit the `KEYWORDS` list or `PARAMS` dictionary in `discord_bot.py`.

---

## 🔒 Security Notes

- All sensitive information (like Bot Token) is managed through the `.env` file
- Ensure `.env` file is included in `.gitignore`
- Never commit files containing sensitive information to version control
