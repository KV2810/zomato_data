import json
from typing import Optional
from pydantic import BaseModel
from parsel import Selector

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
    selector = Selector(f.read())

title = selector.xpath('//h1/text()').get()
print(title)
price = selector.xpath('//p[@class="price_color"]/text()').get()
currency = price[0]
print(currency, price)
price_excl_tax = selector.xpath('//th[text()="Price (excl. tax)"]/following-sibling::td/text()').get()
print(price_excl_tax)
price_incl_tax = selector.xpath('//th[text()="Price (incl. tax)"]/following-sibling::td/text()').get()
print(price_incl_tax)
tax = selector.xpath('//th[text()="Tax"]/following-sibling::td/text()').get()
print(tax)
rating = selector.xpath('//th[text()="Number of reviews"]/following-sibling::td/text()').get()
print(rating)
availability_list = selector.xpath('//p[contains(@class,"availability")]/text()').getall()
availability = "".join(availability_list).strip()
print(availability)
description = selector.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
print(description)
product_type = selector.xpath('//th[text()="Product Type"]/following-sibling::td/text()').get()
print(product_type)
upc = selector.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
print(upc)
product_image_url = selector.xpath('//div[@class="item active"]/img/@src').get()
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
output = BookInfo(
    title=title,
    price=price,
    currency=currency,
    description=description,
    product_image_url=product_image_url,
    product_info=product_info
)
with open("book_scrape/book_info1.json", "w", encoding="utf-8") as f:
    json.dump(output.model_dump(), f, ensure_ascii=False, indent=4)