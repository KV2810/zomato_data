import requests
import mysql.connector as cn
import re
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# Database connection
conn = cn.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="rottentomatoes_db"
)
cursor = conn.cursor()

# Fetch movie URLs
cursor.execute("""
    SELECT m.id, ml.movie_links 
    FROM movie m 
    JOIN movie_links ml ON m.link_id = ml.id
""")
movies = cursor.fetchall()

# Insert query
insert_query = """
INSERT INTO reviews 
(movie_id, critic_name, publication, review_text, review_time, rating) 
VALUES (%s, %s, %s, %s, %s, %s)
"""

for movie_id, url in movies:
    print("\nFetching reviews:", url)

    if url.startswith("/"):
        url = "https://www.rottentomatoes.com" + url

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print("Failed page:", url)
            continue

        # Extract media_id using regex (handles UUID correctly)
        match = re.search(r'"emsId":"([^"]+)"', res.text)

        if not match:
            print("No media ID found:", url)
            continue

        media_id = match.group(1)
        print("Media ID:", media_id)

        # Reviews API
        review_url = f"https://www.rottentomatoes.com/napi/rtcf/v1/movies/{media_id}/reviews?type=critic&pageCount=20"

        while review_url:
            res = requests.get(review_url, headers=headers, timeout=10)

            try:
                data = res.json()
            except:
                print("Invalid JSON response")
                break

            reviews = data.get("reviews", [])

            if not reviews:
                print("No reviews found")
                break

            for item in reviews:
                critic = item.get("critic") or {}
                publication_data = item.get("publication") or {}

                critic_name = critic.get("displayName")
                publication = publication_data.get("name")
                review_text = item.get("reviewQuote")
                raw_time = item.get("createDate")

                review_time = None
                if raw_time:
                    dt = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                    review_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                
                rating_value = item.get("originalScore")

                if not review_text:
                    continue

                # Avoid duplicate entries
                cursor.execute("""
                    SELECT 1 FROM reviews 
                    WHERE movie_id=%s AND critic_name=%s AND review_text=%s
                """, (movie_id, critic_name, review_text))

                if cursor.fetchone():
                    continue

                cursor.execute(insert_query, (
                    movie_id,
                    critic_name,
                    publication,
                    review_text,
                    review_time,
                    rating_value
                ))

            # Pagination handling
            next_link = data.get("links", {}).get("next")

            if next_link:
                review_url = "https://www.rottentomatoes.com" + next_link
            else:
                review_url = None

            time.sleep(1)

    except Exception as e:
        print("Error:", e)

conn.commit()

print("\nReviews data inserted successfully.")

cursor.close()
conn.close()