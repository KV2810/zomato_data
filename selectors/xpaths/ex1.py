from parsel import Selector

html = """
<div>
  <h1>Shoes</h1>
  <p class="price">1000</p>
  <h1>Watch</h1>
  <p class="price">2000</p>
</div>
"""

sel=Selector(text=html)

name=sel.xpath('//h1/text()').get()
price=sel.css('.price::text').get()
print(f"Name: {name},Price:{price}")

name=sel.xpath('//h1/text()').getall()
price=sel.css('.price::text').getall()
print(f"Name: {name},Price:{price}")