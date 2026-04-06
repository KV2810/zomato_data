from lxml import html

html_content = """
<div class="product">
  <h1>Shoes</h1>
  <p class="price">1000</p>
</div>

<div class="product">
  <h1>Watch</h1>
  <p class="price">2000</p>
</div>
"""

tree = html.fromstring(html_content)
products = tree.xpath('//div[@class="product"]')

for product in products:
    name = product.xpath('.//h1/text()')[0]
    price = product.xpath('.//p[@class="price"]/text()')[0]
    print(f"Name: {name}, Price: {price}")  