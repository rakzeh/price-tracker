import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import json
import re

URL = "https://www.amazon.in/OnePlus-Nord-Wired-Earphones-3-5Mm/dp/B0D9NG5Q6R"
TARGET_PRICE = 700  # optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

CSV_FILE = "price_history.csv"

def fetch_page():
    r = requests.get(URL, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.text

def extract_price_from_jsonld(html):
    scripts = re.findall(r'<script type="application/ld\\+json">(.*?)</script>', html, re.S)
    for s in scripts:
        try:
            data = json.loads(s)
            offers = data.get("offers", {})
            price = offers.get("price")
            if price:
                return int(float(price))
        except Exception:
            pass
    return None

def extract_price_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    price = soup.select_one("span.a-offscreen")
    if price:
        text = price.text.replace("₹", "").replace(",", "").strip()
        return int(float(text))
    return None

def get_price():
    html = fetch_page()

    # 1️⃣ Try structured data (MOST STABLE)
    price = extract_price_from_jsonld(html)
    if price:
        return price

    # 2️⃣ Fallback to HTML
    price = extract_price_from_html(html)
    if price:
        return price

    # 3️⃣ Save debug HTML (for future fix)
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    return None

def save_price(price):
    exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "price"])
        writer.writerow([datetime.utcnow().isoformat(), price])

def main():
    price = get_price()

    if price is None:
        print("Price not found – skipping this run (safe)")
        return

    save_price(price)
    print(f"Current price: ₹{price}")

    if price <= TARGET_PRICE:
        print("TARGET PRICE HIT")

if __name__ == "__main__":
    main()
