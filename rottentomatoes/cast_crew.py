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

query = """insert ignore into cast_crew(movie_id, person_name, role_type, role, character_name) values (%s, %s, %s, %s, %s)"""

for movie_id,url in movies:
    print("Fetching:", url)
    
    if url.startswith("/"):
        url = "https://www.rottentomatoes.com" + url

    cast_url = url.rstrip("/") + "/cast-and-crew"

    try:
       
        res = requests.get(cast_url, headers=headers, timeout=10)
        print("review-card-critic" in res.text)

        if res.status_code != 200:
            print("Failed:", url)
            continue

        tree = html.fromstring(res.text)
        
        person_names=tree.xpath("//cast-and-crew-card//rt-text[contains(@slot,'title')][1]//text()")
        print("CAST:", person_names) 
        character_names=tree.xpath("//cast-and-crew-card/rt-text[contains(@slot,'characters')]//text()")
        print("CHARACTER:", character_names)
        credits=tree.xpath("//cast-and-crew-card/rt-text[contains(@slot,'credits')]//text()")
        print("CREDITS:", credits)
       

        for i in range(len(person_names)):
            name = person_names[i].strip()
            character = character_names[i].strip() if i < len(character_names) else None
            role=credits[i].strip() if i < len(credits) else None

            cursor.execute(query, (movie_id,name,"cast",role,character))
        
        person_names=tree.xpath("//cast-and-crew-card/rt-text[contains(@slot,'title')][1]/text()")
        print("CREDITS:", credits)


        for i in range(len(person_names)):
            name = person_names[i].strip()
            role=credits[i].strip() if i < len(credits) else None

            cursor.execute(query, (movie_id,name,"crew",role,None))


    except Exception as e:
        print("Error:", e)
        
conn.commit()

print("Cast and Crew data inserted successfully!")

cursor.close()
conn.close()