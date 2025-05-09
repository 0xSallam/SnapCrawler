# SnapCrawler

A lightweight Python CLI tool that crawls a website, takes full-page screenshots of each page up to a given depth, and outputs link data in JSON, CSV or plain text.

## 🚀 Features

- **Breadth-first crawl** of a single host up to configurable depth  
- **Respectful**: honors `robots.txt` and customizable delay between requests  
- **Headless screenshots** via Playwright (Chromium)  
- **Multi-format output**: JSON, CSV or simple text logs  
- **Customizable User-Agent** string  

## 🛠️ Requirements

- Python 3.8+  
- [Playwright](https://playwright.dev/python/) (Chromium)  
- `requests`  
- `beautifulsoup4`
- `Playwright`

## 💡 Installation
```
git clone https://github.com/0xSallam/SnapCrawler.git
cd SnapCrawler
python -m venv venv            # optional virtualenv
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```
## 📖 Usage
```
python SnapCrawler.py <start_url> [options]

| Flag             | Description                         | Default           |
| ---------------- | ----------------------------------- | ----------------- |
|  <start_url>     | Starting page for the crawl         | —                 |
|  -d, --depth     | Max crawl depth                     | 2                 |
|  -o, --output    | Path to save results (json/csv/txt) | results.txt       |
|  --delay         | Seconds to wait between requests    | 1.0               |
|  --user-agent    | Custom User-Agent header            | LinkCrawler/1.0   |
```
## Examples 
```
python SnapCrawler.py https://example.com -d 2 --delay 0.5 -o example.json
python SnapCrawler.py https://example.com -o example.csv
python SnapCrawler.py https://example.com --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0)"
```
Screenshots will end up in ./screenshots/ by default.

## ⚙️ How It Works
1. Fetch robots.txt and check crawl permissions 
2. BFS queue: start URL → discovered links (same host)
3. Playwright loads each URL → captures a full-page PNG
4. Requests fetches HTML → BeautifulSoup extracts further links
5. Delay ensures respectful crawling
