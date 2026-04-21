from textwrap import indent
import requests
import json

url = "https://v2.sg.media-imdb.com/suggestion/x/x.json"

res = requests.get(url)
    
with open("imdb/imdb.json","w") as f:
    json.dump(res.text,f,indent=4)
