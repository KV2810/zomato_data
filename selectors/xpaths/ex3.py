from bs4 import BeautifulSoup

html = """
<html>
  <body>
    <div id="main">
      <div class="product" data-id="101">
        <h2>Phone</h2>
        <p class="price">50000</p>
        <a href="buy.com/phone">Buy</a>
      </div>

      <div class="product" data-id="102">
        <h2>Laptop</h2>
        <p class="price">80000</p>
        <a href="buy.com/laptop">Buy</a>
      </div>
    </div>
  </body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

products = soup.find_all('div', class_='product')

data = []

for p in products:
    item = {
        "name": p.find('h2').text,
        "price": p.find('p', class_='price').text,
        "link": p.find('a')['href'],
        "id": p.get('data-id')
    }
    data.append(item)

print(data)