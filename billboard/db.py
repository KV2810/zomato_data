from lxml import html
import mysql.connector
from datetime import datetime

# -------------------------------
# HELPER FUNCTION TO CONVERT DATE FORMAT
# -------------------------------
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

# -------------------------------
# LOAD FILE
# -------------------------------
with open("billboard.html", "r", encoding="utf-8") as f:
    tree = html.fromstring(f.read())

# -------------------------------
# DB CONNECTION
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="billboard_db"
)
cursor = conn.cursor()

# -------------------------------
# CHECK IF DATA ALREADY EXISTS FOR TODAY
# -------------------------------
cursor.execute("SELECT COUNT(*) FROM billboards WHERE scraped_date = CURDATE()")
existing_count = cursor.fetchone()[0]
if existing_count >= 100:
    print(f"[INFO] Data for today already exists ({existing_count} songs). Existing rows will be updated.")

# -------------------------------
# FIND SONG BLOCKS
# -------------------------------
songs = tree.xpath('//div[contains(@class,"o-chart-results-list-row-container")]')

print(f"Found {len(songs)} songs to process")

seen = set()
count = 0

for song in songs:

    # -------------------------------
    # RANK
    # -------------------------------
    rank = song.xpath('.//ul[contains(@class,"o-chart-results-list-row")]//li[contains(@class,"o-chart-results-list__item")][1]//span/text()')
    rank = [r.strip() for r in rank if r.strip().isdigit()]
    rank = rank[0] if rank else None

    print(f"Processing song with extracted rank: {rank}")

    if not rank or rank in seen:
        print(f"Skipping song with rank {rank} (already seen or invalid)")
        continue
    seen.add(rank)

    # -------------------------------
    # TITLE
    # -------------------------------
    title = song.xpath('.//h3[@id="title-of-a-story"]/text()')
    title = [t.strip() for t in title if t.strip()]
    title = title[0] if title else None

    # -------------------------------
    # ARTIST
    # -------------------------------
    artist = song.xpath('.//span[contains(@class,"a-no-trucate")]//text()')
    artist = [a.strip() for a in artist if a.strip()]
    artist = artist[0] if artist else None

    # -------------------------------
    # LW / PEAK / WEEKS
    # -------------------------------
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

    # -------------------------------
    # DEBUT POSITION
    # -------------------------------
    debut_position = None
    dp = song.xpath('.//h3[contains(text(),"Debut Position")]/following::span[1]//text()')
    dp = [d.strip() for d in dp if d.strip()]
    if dp:
        debut_position = dp[0]

    # -------------------------------
    # DEBUT CHART DATE
    # -------------------------------
    debut_chart_date = None
    dcd = song.xpath('.//h4[contains(text(),"Debut Chart Date")]/following::span[1]//a/text()')
    dcd = [d.strip() for d in dcd if d.strip()]
    if dcd:
        debut_chart_date = convert_date(dcd[0])

    # -------------------------------
    # PEAK CHART DATE
    # -------------------------------
    peak_chart_date = None
    peak_date = None
    pcd = song.xpath('.//h4[contains(text(),"Peak Chart Date")]/following::span[1]//a/text()')
    pcd = [p.strip() for p in pcd if p.strip()]
    if pcd:
        peak_chart_date = convert_date(pcd[0])
        peak_date = convert_date(pcd[0])

    # -------------------------------
    # AWARDS (FINAL FIX)
    # -------------------------------
    awards = song.xpath('.//div[contains(@class,"o-chart-awards-list-item")]//p[contains(@class,"c-tagline")]//text()')
    awards = [a.strip() for a in awards if a.strip()]
    awards = ", ".join(awards) if awards else None

    # -------------------------------
    # INSERT
    # -------------------------------
    if title and artist and rank:

        query = """
        INSERT INTO billboards
        (rank_position, song_title, artist, last_week, peak_position, weeks_on_chart,
         debut_position, debut_chart_date, peak_date, peak_chart_date, awards, scraped_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
        ON DUPLICATE KEY UPDATE
        song_title = VALUES(song_title),
        artist = VALUES(artist),
        last_week = VALUES(last_week),
        peak_position = VALUES(peak_position),
        weeks_on_chart = VALUES(weeks_on_chart),
        debut_position = VALUES(debut_position),
        debut_chart_date = VALUES(debut_chart_date),
        peak_date = VALUES(peak_date),
        peak_chart_date = VALUES(peak_chart_date),
        awards = VALUES(awards)
        """

        cursor.execute(query, (
            rank, title, artist,
            last_week, peak, weeks,
            debut_position, debut_chart_date, peak_date, peak_chart_date,
            awards
        ))

        # Check if this was an insert (1) or update (2)
        if cursor.rowcount == 1:
            print(f"[INSERTED] {rank}. {title} - {artist}")
            count += 1
        else:
            print(f"[UPDATED] {rank}. {title} - {artist}")


conn.commit()
cursor.close()
conn.close()

print(f"\n[DONE] {count} songs inserted successfully!")