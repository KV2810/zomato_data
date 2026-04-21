import requests
from bs4 import BeautifulSoup
import mysql.connector

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="billboard_db"
)

cursor = conn.cursor()

# -------------------------------
# URL + HEADERS (IMPORTANT)
# -------------------------------
BASE_URL = "https://www.billboard.com/charts/hot-100/"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}
with open("billboard/billboard.html", "r", encoding="utf-8") as f:
    html_content = f.read()
response = requests.get(BASE_URL, data=html_content, headers=headers)

# Check response
if response.status_code != 200:
    print("Failed to fetch page")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# -------------------------------
# SCRAPE DATA
# -------------------------------
songs = soup.select("li.o-chart-results-list__item")

rank = 1

for song in songs:
    try:
        title_tag = song.select_one("h3")
        artist_tag = song.select_one("span.c-label")

        if title_tag and artist_tag:
            title = title_tag.text.strip()
            artist = artist_tag.text.strip()

            # Insert into DB
            query = """
            INSERT INTO billboards (rank_position, song_title, artist,scraped_date)
            VALUES (%s, %s, %s, CURDATE())
            """

            cursor.execute(query, (rank, title, artist))

            print(rank, title, "-", artist)

            rank += 1

    except Exception as e:
        print("Error:", e)

# -------------------------------
# SAVE DATA
# -------------------------------
conn.commit()

cursor.close()
conn.close()

print(" Data inserted successfully!")