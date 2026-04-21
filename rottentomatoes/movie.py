import requests
from lxml import html
import mysql.connector as cn

headers = {
    "User-Agent": "Mozilla/5.0"
}

conn=cn.connect(host="localhost",user="root",password="actowiz",database="rottentomatoes_db")
cursor=conn.cursor()

cursor.execute("SELECT id,movie_links FROM movie_links")
movie_links = cursor.fetchall()

query="insert into movie(name,description,poster_image,rating,link_id) values(%s,%s,%s,%s,%s)"

for link_id, url in movie_links:
    print("Scraping:", url)

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print("Failed:", url)
            continue

        tree = html.fromstring(res.text) 
        name = tree.xpath("//media-hero/rt-text[contains(@slot,'title')][1]/text()")
        name=name[0] if name else None
        print(name)
        description = tree.xpath("//drawer-more//rt-text[1]/text()")
        description = description[0] if description else None
        print(description)

        poster=tree.xpath('//media-scorecard//rt-img/@src')
        poster = poster[0] if poster else "None"
        print(poster)

        rating=tree.xpath("//media-scorecard//rt-text[contains(@slot,'critics-score')][1]/text()")
        rating = rating[0] if rating else None
        print("Rating:", rating)
    
        cursor.execute(query, (name,description,poster,rating,link_id))

    except Exception as e:
        print("Error:", e)

conn.commit()

print("Movie data inserted successfully!")

cursor.close()
conn.close()
