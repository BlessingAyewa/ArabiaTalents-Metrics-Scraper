# Video Stats Scraper 📊

An automated Python tool that scrapes engagement metrics (Views, Likes, Comments) from **YouTube**, **TikTok**, and **Facebook**, and updates a **Google Sheet** in real-time.

---

## 🛠 Features
* **Multi-Platform:** Support for YouTube (via API), TikTok (via Rehydration Data), and Facebook (via Playwright).
* **Async Performance:** Built with `asyncio`, `aiohttp`, and `Playwright` for high-speed concurrent scraping.
* **Google Sheets Integration:** Automatically reads video links and writes back updated stats.
* **GitHub Actions Ready:** Includes a workflow for scheduled daily updates with automated caching.

---

## 🚀 Local Setup

### 1. Prerequisites
* Python 3.10+
* Google Cloud Service Account JSON (`goolglesheet-connect.json`)
* YouTube Data API v3 Key

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd video-stats-scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium --with-deps