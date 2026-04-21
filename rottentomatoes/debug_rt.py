import requests
from lxml import html

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.rottentomatoes.com/m/the_batman/reviews"
res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Length of content:", len(res.text))
print("review-card-critic in text:", "review-card-critic" in res.text)

with open("debug_reviews.html", "w", encoding="utf-8") as f:
    f.write(res.text)

tree = html.fromstring(res.text)
critics = tree.xpath("//review-card-critic//rt-link[contains(@slot,'name')]/text()")
print("Critics found:", critics)
