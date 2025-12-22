import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

URL = "https://www.amazon.in/OnePlus-Nord-Wired-Earphones-3-5Mm/dp/B0D9NG5Q6R"
TARGET_PRICE = 700  # change this

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9"
}

def get_price():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    price = soup.select_one("span.a-price-whole")
    if not price:
        raise Exception("Price not found")

    price = price.text.replace(",", "").strip()
    return int(price)

def save_price(price):
    exists = os.path.isfile("price_history.csv")
    with open("price_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["time", "price"])
        writer.writerow([datetime.now().isoformat(), price])

if __name__ == "__main__":
    price = get_price()
    save_price(price)
    print(f"Current price: ₹{price}")

    if price <= TARGET_PRICE:
        print("PRICE DROP!")
