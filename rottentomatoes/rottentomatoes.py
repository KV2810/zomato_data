import requests
import mysql.connector as cn
from lxml import html

BASE_API = "https://www.rottentomatoes.com/browse/movies_in_theaters/sort:newest"

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}

all_links = set()
for page in range(1, 6):  
    url = f"{BASE_API}?page={page}"
    print("Fetching:", url)

    res=requests.get(url,headers=headers)
    tree=html.fromstring(res.text)


    links = tree.xpath('//a[contains(@href, "/m/")]/@href')
    if not links:
        break

    for link in links:
        full_link = "https://www.rottentomatoes.com" + link
        all_links.add(full_link)
        
all_links = list(all_links)
print("Total links:", len(all_links))
conn = cn.connect(host="localhost",user="root",password="actowiz",database="rottentomatoes_db")
cursor = conn.cursor()

query = "insert into movie_links (movie_links) values (%s)"

for link in all_links:
    cursor.execute(query, (link,))

conn.commit()

print("All links inserted!")

cursor.close()
conn.close()