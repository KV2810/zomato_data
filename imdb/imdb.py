from lxml import html
import mysql.connector as cn
import re
import json

with open("imdb/imdb.html","r",encoding="utf-8") as f:
    content = f.read()

conn=cn.connect(host="localhost",username="root",port="3306",password="actowiz",database="imdb_db")
cursor=conn.cursor()

match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content)
count=0

if match:
    data=json.loads(match.group(1))

    movies=data["itemListElement"]

    for movie in movies:
        item=movie["item"]

        title=item["name"]
        url=item["url"]
        rating=item["aggregateRating"]["ratingValue"]
        votes=item["aggregateRating"]["ratingCount"]

        print(title,url,rating,votes)

        query="""
        insert into imdb (title,movie_url,rating,votes) values(%s,%s,%s,%s)
        """
        cursor.execute(query,(title,url,rating,votes))
        conn.commit()
        count+=1

cursor.close()
conn.close()

print("\n[DONE]",count,"movies inserted successfully!")