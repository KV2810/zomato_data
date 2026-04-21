import re
import json

# read saved file
with open("imdb/imdb.html", "r", encoding="utf-8") as f:
    html = f.read()

# extract JSON inside script
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html)

if match:
    data = json.loads(match.group(1))

    movies = data["itemListElement"]

    for i, movie in enumerate(movies, start=1):
        item = movie["item"]

        title = item["name"]
        url = item["url"]
        rating = item["aggregateRating"]["ratingValue"]
        votes = item["aggregateRating"]["ratingCount"]

        print(i, title, rating, votes, url)