import json
from lxml import html
from pydantic import BaseModel
from typing import Optional

class ProductInfo(BaseModel):
    upc: Optional[str] 
    product_type: Optional[str]
    price_excl_tax: str
    price_incl_tax: str
    tax: str
    availability: str
    rating: int

class BookInfo(BaseModel):
    title: str 
    price: str 
    currency: str 
    description: str
    product_image_url: Optional[str] 
    product_info: ProductInfo

with open("book_scrape/book.html", "r", encoding="utf-8") as f:
    tree= html.fromstring(f.read())

title = tree.xpath('//h1/text()')[0]
print(title)
price=tree.xpath('//p[@class="price_color"]/text()')[0]
currency = price[0]
print(currency,price)
price_excl_tax = tree.xpath('//th[text()="Price (excl. tax)"]/following-sibling::td/text()')[0]
print(price_excl_tax)       
price_incl_tax = tree.xpath('//th[text()="Price (incl. tax)"]/following-sibling::td/text()')[0]
print(price_incl_tax)
tax = tree.xpath('//th[text()="Tax"]/following-sibling::td/text()')[0]
print(tax)
rating=tree.xpath('//th[text()="Number of reviews"]/following-sibling::td/text()')[0]
print(rating)
availability_list = tree.xpath('//p[contains(@class,"availability")]/text()')
availability = "".join(availability_list).strip()
print(availability)
description = tree.xpath("//div[@id='product_description']/following-sibling::p/text()")[0]
print(description)
product_type = tree.xpath('//th[text()="Product Type"]/following-sibling::td/text()')[0]
print(product_type)
upc = tree.xpath('//th[text()="UPC"]/following-sibling::td/text()')[0]
print(upc)
product_image_url = tree.xpath('//div[@class="item active"]/img/@src')[0]
print(product_image_url)

product_info = ProductInfo(
    upc=upc,
    product_type=product_type,
    price_excl_tax=price_excl_tax,
    price_incl_tax=price_incl_tax,
    tax=tax,
    availability=availability,
    rating=int(rating)
)

output=BookInfo(
    title=title,
    price=price,
    currency=currency,
    description=description,
    product_image_url=product_image_url,
    product_info=product_info
)

with open("book_scrape/book_info.json", "w", encoding="utf-8") as f:
    json.dump(output.model_dump(), f, ensure_ascii=False, indent=4)

print(output)