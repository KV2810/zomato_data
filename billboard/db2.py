import mysql.connector as cn
import requests
from lxml import html
from datetime import datetime

def convert_date(date_str):
    """Convert MM/DD/YY to YYYY-MM-DD format"""
    if not date_str:
        return None
    try:
        # Parse MM/DD/YY format
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        # Convert to YYYY-MM-DD format
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None

with open("billboard/billboard.html", "r", encoding="utf-8") as f:
    tree=html.fromstring(f.read())

conn=cn.Connect(host="localhost",user="root",port="3306",password="actowiz",database="billboards_db")
cursor=conn.cursor()

songs=tree.xpath("//div[contains(@class,'o-chart-results-list-row-container')]")
print(len(songs))

seen=set()
count=0

for song in songs:
    #Rank
    rank=song.xpath(".//ul[contains(@class,'o-chart-results-list-row')]//li[contains(@class,'o-chart-results-list__item ')][1]//span/text()")
    rank=[r.strip() for r in rank if r.strip().isdigit()]
    rank=rank[0] if rank else None
    print("Rank:",rank)

    if not rank or rank in seen:
        print(f"Skipping song with rank {rank} (already seen or invalid)")
        continue
    seen.add(rank)

    #Song Name
    title=song.xpath(".//h3[@id='title-of-a-story']/text()")
    title=[t.strip() for t in title if t.strip()]
    title=title[0] if title else None
    print("Title:",title)

    #Arist Name
    artist=song.xpath(".//span[contains(@class,'a-no-trucate')]//text()")
    artist=[a.strip() for a in artist if a.strip()]
    artist=artist[0] if artist else None
    print("Artist:",artist)

    #Last Week,Peak,Weeks
    labels = song.xpath('.//span/text()')
    labels = [l.strip() for l in labels if l.strip()]

    last_week = peak = weeks = None

    for i in range(len(labels)):
        if labels[i] == "LW":
            last_week = labels[i+1] if i+1 < len(labels) else None
        elif labels[i] == "PEAK":
            peak = labels[i+1] if i+1 < len(labels) else None
        elif labels[i] == "WEEKS":
            weeks = labels[i+1] if i+1 < len(labels) else None

    #Debut Position
    debut_position=None
    dp=song.xpath(".//h3[contains(text(),'Debut Positio')]/following::span[1]//text()")
    dp=[d.strip() for d in dp if d.strip()]
    if dp:
        debut_position = dp[0]
        print("Debut Position:",debut_position)

    #Debut Chart Date
    debut_chart_date=None
    dcd=song.xpath(".//h4[contains(text(),'Debut Chart Date')]/following::span[1]//a/text()")
    dcd=[dd.strip() for dd in dcd if dd.strip()]
    if dcd:
        debut_chart_date=convert_date(dcd[0])
        print("Debut Chart Date:",debut_chart_date)

    #Peak Position
    peak_position=None
    pk=song.xpath(".//h3[contains(text(),'Peak Position')]/following::span[1]//text()")
    pk=[p.strip() for p in pk if p.strip()]
    if pk:
        peak_position=pk[0]
        print("Peak Position:",peak_position)

    #Peak Chart Date
    peak_chart_date=None
    pcd=song.xpath(".//h4[contains(text(),'Peak Chart Date')]/following::span[1]//a/text()")
    pcd=[pc.strip() for pc in pcd if pc.strip()]
    if pcd:
        peak_chart_date=convert_date(pcd[0])
        print("Peak Chart Date:",peak_chart_date)

    #Awards
    awards=song.xpath(".//div[contains(@class,'o-chart-awards-list-item')]//p[contains(@class,'c-tagline ')]//text()")
    awards=[a.strip() for a in awards if a.strip()]
    awards = ", ".join(awards) if awards else None
    print("Awards:",awards)

    if title and artist and rank:
        query="""
        insert into billboard_new (rank_no,title,artist,last_week,peak_position,weeks_on_chart,awards,
        debut_position,debut_chart_date,peak_chart_date) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """  
        cursor.execute(query, (
        rank,
        title,
        artist,
        last_week,
        peak,
        weeks,
        awards,
        debut_position, 
        debut_chart_date,
        peak_chart_date
        ))
        count+=1

conn.commit()
cursor.close()
conn.close()

print(f"\n[DONE] {count} songs inserted successfully!") 