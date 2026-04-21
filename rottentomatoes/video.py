import requests
from lxml import html
import mysql.connector as cn

headers = {
    "User-Agent": "Mozilla/5.0"
}

conn=cn.connect(host="localhost",user="root",password="actowiz",database="rottentomatoes_db")
cursor=conn.cursor()

cursor.execute("""select m.id, ml.movie_links from movie m join movie_links ml on m.link_id = ml.id""")
movies = cursor.fetchall()

query = """insert ignore into videos (movie_id, video_url) values(%s, %s)"""

for movie_id, url in movies:
    print("Fetching videos:", url)

    if url.startswith("/"):
        url = "https://www.rottentomatoes.com" + url

    video_page = url.rstrip("/") + "/videos"

    try:
        res = requests.get(video_page, headers=headers, timeout=10)

        if res.status_code != 200:
            continue

        tree = html.fromstring(res.text)
        video_links = tree.xpath('//a[contains(@href, "/videos")]/@href')
        video_links = list(set(video_links))
        print("Video links:", video_links)

        for link in video_links:
            full_link = "https://www.rottentomatoes.com" + link

            cursor.execute(query, (movie_id, full_link))

    except Exception as e:
        print("Error:", e)

conn.commit()

print("Video links inserted successfully!")

cursor.close()
conn.close()