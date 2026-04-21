from lxml import html
import json

with open("rottentomatoes/newest.html", "r", encoding="utf-8") as f:
    tree = html.fromstring(f.read())


script = tree.xpath("//script[@type='application/ld+json']/text()")[0]
json_data = script
data = json.loads(json_data)

with open("rottentomatoes/output1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("JSON file created successfully!")