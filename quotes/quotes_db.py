import requests
from bs4 import BeautifulSoup
import mysql.connector

#Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",   
    database="quotes_db"
)

cursor = conn.cursor()

BASE_URL = "https://quotes.toscrape.com"

page = 1

while True:
    url = f"{BASE_URL}/page/{page}/"
    print(f"Scraping Page {page}...")

    response = requests.get(url)
    
    if response.status_code != 200:
        print("No more pages to scrape.")
        break

    soup = BeautifulSoup(response.text, 'html.parser')

    quotes = soup.find_all('div', class_='quote')

    if not quotes:
        print("No more quotes found.")
        break

    for quote in quotes:
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()
        tags_list = quote.find_all("a", class_="tag")
        tags = ", ".join([tag.text for tag in tags_list])

        query = """
        INSERT INTO quotes (quote, author, tags)
        VALUES (%s, %s, %s)
        """
        values = (text, author, tags)

        cursor.execute(query, values)
    conn.commit()
    page += 1

print("Scraping Completed!")

cursor.close()
conn.close()