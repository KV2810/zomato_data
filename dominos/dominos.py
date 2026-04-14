import requests

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.google.com/',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    # 'cookie': 'marketingChannel=https://www.google.com/ / Organic; brandreferral=yes; _gcl_au=1.1.609983398.1773643210; _ga=GA1.3.660372443.1773643215; _fbp=fb.2.1773643216009.577435171746527104; amp_ff201f=GGRN7w_lFX5uGaC1nYuWmr...1jlqu9dfd.1jlqu9h2d.8.9.h; _gid=GA1.3.1058232551.1775799437; WZRK_S_44Z-RW9-694Z=%7B%22p%22%3A1%7D; _uetsid=566c93f0349f11f1abe22f0bb86064e1; _uetvid=feaedd70210211f1bb735596447a8e4a; _ga_HX7QKSMSZY=GS2.3.s1775799438$o3$g0$t1775799438$j60$l0$h0; _ga_SBQSVGZ30L=GS2.3.s1775799438$o3$g0$t1775799438$j60$l0$h0',
}

response = requests.get('https://www.dominos.co.in/store-location/', headers=headers)
#print(response.text)

with open("dominos/dominos.html", "w", encoding="utf-8") as f:
    f.write(response.text)