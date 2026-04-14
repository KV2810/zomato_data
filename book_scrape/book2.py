import json
from typing import Optional
from pydantic import BaseModel
from bs4 import BeautifulSoup

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
    soup = BeautifulSoup(f, "html.parser")

title = soup.find("h1").text
print(title)
price = soup.find("p", class_="price_color").text
currency = price[0]
print(currency, price)
price_excl_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").text
print(price_excl_tax)
price_incl_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").text
print(price_incl_tax)
tax = soup.find("th", text="Tax").find_next_sibling("td").text
print(tax)
rating = soup.find("th", text="Number of reviews").find_next_sibling("td").text
print(rating)
availability_list = soup.find("p", class_="availability").text
availability = "".join(availability_list).strip()
print(availability)
description = soup.find("div", id="product_description").find_next_sibling("p").text
print(description)
product_type = soup.find("th", text="Product Type").find_next_sibling("td").text
print(product_type)         
upc = soup.find("th", text="UPC").find_next_sibling("td").text
print(upc)
product_image_url = soup.find("div", class_="item active").find("img")["src"]
print(product_image_url)

product_info = ProductInfo(
    upc=upc,
    product_type=product_type,
    price_excl_tax=price_excl_tax,
    price_incl_tax=price_incl_tax,
    tax=tax,
    availability=availability,
    rating=rating
)   

output = BookInfo(
    title=title,
    price=price,
    currency=currency,
    description=description,
    product_image_url=product_image_url,
    product_info=product_info   
)           

with open("book_scrape/output.json", "w", encoding="utf-8") as f:
    json.dump(output.model_dump(), f, indent=4)