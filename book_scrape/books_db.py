import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import mysql.connector
import time
import sys
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"


# CONNECT TO MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",   
    database="books_db"
)

cursor = conn.cursor(buffered=True)

# Create requests session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,  # Retry up to 3 times
    backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


# SCRAPE BOOK LINKS

def scrape_links():
    url = BASE_URL

    while True:
        print(f"Scraping page: {url}")
        try:
            res = session.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"   Error fetching {url}: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        books = soup.select("article.product_pod h3 a")

        for book in books:
            link = book.get("href")
            full_link = urljoin(url, link)

            # Check if link already exists to prevent duplicates
            cursor.execute("SELECT id FROM book_links WHERE book_url = %s", (full_link,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO book_links (book_url) VALUES (%s)",
                    (full_link,)
                )

        conn.commit()

        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_url = next_btn.get("href")
            url = urljoin(url, next_url)
        else:
            break

# SCRAPE BOOK DETAILS
def get_tag_text(tag, default=""):
    return tag.text.strip() if tag else default


def scrape_book_details():
    cursor.execute("SELECT id, book_url FROM book_links WHERE is_scraped=FALSE")
    rows = cursor.fetchall()

    for row in rows:
        book_id, url = row
        print(f"Scraping book: {url}")

        try:
            res = session.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"   Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        title = get_tag_text(soup.find("h1"))
        price = get_tag_text(soup.find("p", class_="price_color"))
        availability = get_tag_text(soup.find("p", class_="instock availability"))
        rating_tag = soup.find("p", class_="star-rating")
        rating = rating_tag["class"][1] if rating_tag and len(rating_tag.get("class", [])) > 1 else ""

        description_tag = soup.find("div", id="product_description")
        description = get_tag_text(description_tag.find_next_sibling("p")) if description_tag else ""

        breadcrumb_links = soup.select("ul.breadcrumb li a")
        category = breadcrumb_links[2].text.strip() if len(breadcrumb_links) > 2 else ""

        image_tag = soup.find("img")
        image_src = image_tag.get("src") if image_tag else ""
        image_url = urljoin(url, image_src) if image_src else ""

        # Check if book already exists in the books table
        cursor.execute("SELECT id FROM books WHERE product_url = %s", (url,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO books (title, price, availability, rating, description, category, image_url, product_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                title, price, availability, rating,
                description, category, image_url, url
            ))

        cursor.execute(
            "UPDATE book_links SET is_scraped=TRUE WHERE id=%s",
            (book_id,)
        )

        conn.commit()
        time.sleep(0.5)


# RESET FUNCTION
def reset_scraped_flag():
    """Reset is_scraped flag to FALSE for all book_links"""
    confirm = input("⚠️  This will reset all scraped books to FALSE. Continue? (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("UPDATE book_links SET is_scraped=FALSE")
        conn.commit()
        print(" Reset completed! All books marked as not scraped.")
    else:
        print("Reset cancelled.")


# CLEAR TABLES FUNCTION
def clear_tables():
    """Completely empty the books and book_links tables"""
    confirm = input("⚠️  This will completely DELETE ALL DATA in your tables. Continue? (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("TRUNCATE TABLE book_links")
        cursor.execute("TRUNCATE TABLE books")
        conn.commit()
        print("🗑️  Tables cleared successfully!")
    else:
        print("Clear cancelled.")

# RUN

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            reset_scraped_flag()
        elif sys.argv[1] == "--clear":
            clear_tables()
    else:
        scrape_links()
        scrape_book_details()
        print(" Scraping Completed!")