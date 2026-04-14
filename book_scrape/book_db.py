import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"

# -------------------------------
# 1. CONNECT TO SQLITE DATABASE
# -------------------------------
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# -------------------------------
# 2. CREATE TABLES
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS book_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_url TEXT,
    is_scraped INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price TEXT,
    availability TEXT,
    rating TEXT,
    description TEXT,
    category TEXT,
    image_url TEXT,
    product_url TEXT
)
""")

conn.commit()

# -------------------------------
# 3. SCRAPE ALL BOOK LINKS
# -------------------------------
def scrape_links():
    url = BASE_URL

    while True:
        print(f"Scraping page: {url}")
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch page {url}. Error: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        books = soup.select("article.product_pod h3 a")

        for book in books:
            link = book.get("href")
            full_link = urljoin(url, link)

            cursor.execute("INSERT INTO book_links (book_url) VALUES (?)", (full_link,))
        
        conn.commit()

        # Next page
        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_url = next_btn.get("href")
            url = urljoin(url, next_url)
        else:
            break

# -------------------------------
# 4. SCRAPE BOOK DETAILS
# -------------------------------
def scrape_book_details():
    cursor.execute("SELECT id, book_url FROM book_links WHERE is_scraped=0")
    rows = cursor.fetchall()

    for row in rows:
        book_id, url = row
        print(f"Scraping book: {url}")

        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch book {url}. Error: {e}. Skipping.")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.text if title_tag else "N/A"

        price_tag = soup.find("p", class_="price_color")
        price = price_tag.text if price_tag else "N/A"

        avail_tag = soup.find("p", class_="instock availability")
        availability = avail_tag.text.strip() if avail_tag else "N/A"

        rating_tag = soup.find("p", class_="star-rating")
        rating = rating_tag["class"][1] if rating_tag and len(rating_tag.get("class", [])) > 1 else "N/A"

        description_tag = soup.find("div", id="product_description")
        description = description_tag.find_next_sibling("p").text if description_tag and description_tag.find_next_sibling("p") else ""

        breadcrumb = soup.select("ul.breadcrumb li a")
        category = breadcrumb[2].text if len(breadcrumb) > 2 else "N/A"

        image_tag = soup.find("img")
        image_url = urljoin(url, image_tag["src"]) if image_tag else ""

        # Insert into books table
        cursor.execute("""
        INSERT INTO books (title, price, availability, rating, description, category, image_url, product_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, price, availability, rating, description, category, image_url, url))

        # Mark as scraped
        cursor.execute("UPDATE book_links SET is_scraped=1 WHERE id=?", (book_id,))
        conn.commit()

        time.sleep(0.5)  # polite scraping

# -------------------------------
# 5. RUN EVERYTHING
# -------------------------------
scrape_links()
scrape_book_details()

print("✅ Scraping Completed!")