from bs4 import BeautifulSoup

html="""
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

soup=BeautifulSoup(html,"html.parser")

products=soup.find_all('h2')
for product in products:
    print(product.text)

products=soup.find('h2')
print(products.text)

print("\n----- CSS SELECT -----")
products_css = soup.select('.product')
print(products_css)

print("\n----- SELECT ONE -----")
first_css = soup.select_one('.product')
print(first_css)

print("\n----- ALL ATTRIBUTES -----")
product_div = soup.find('div', class_='product')
print(product_div.attrs)

print("\n----- PRICES -----")
price = soup.select('.price')
for p in price:
    print(p.text)