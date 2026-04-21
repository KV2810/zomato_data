import json
from pydantic import BaseModel
from typing import List, Optional, Union, Dict
from lxml import html

# ---------------- MODELS ----------------

class Query(BaseModel):
    partno: str
    categoryName: str
    shape: str

class Dimensions(BaseModel):
    d1: float
    d2: float
    b1: float

class Technical_Attribues(BaseModel):
    description: str
    value: Union[str, bool]
    icon: Optional[str] = None

class Technical_Data(BaseModel):
    name: str
    label: str
    attributes: List[Technical_Attribues]

class Product(BaseModel):
    title: str
    query: Query
    img: str
    singleUsp: str
    dimensions: Dimensions
    manufacturing_method: str
    material_properties: List[str]
    quantity: int
    unit: str
    totalPrice: float = 0
    unitPrice: float = 0
    setupCost: float = 0
    product_description: Dict[str, str]
    technical_data: List[Technical_Data]

# ---------------- READ HTML ----------------

with open("igus/igus.html", "r", encoding="utf-8") as f:
    data = f.read()

tree = html.fromstring(data)

# ---------------- EXTRACT NEXT DATA ----------------

script = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
data2 = json.loads(script)

all_data = data2.get('props', {}).get('pageProps', {})
query_data = data2.get('query', {})

# ---------------- BASIC FIELDS ----------------

title = all_data.get('akeneoProductData', {}).get('title', "")

# PART NUMBER (from JSON fallback to meta)
partno = (
    query_data.get('partno')
    or all_data.get('articleData', {}).get('articleNumber')
    or tree.xpath("//meta[@name='sis-tag_article-number']/@content")[0]
)

shape = query_data.get('shape', "")
category = query_data.get('categoryName', "")

# IMAGE (JSON fallback → meta)
img_url = (
    all_data.get('akeneoProductData', {}).get('mainImage')
    or tree.xpath("//meta[@property='og:image']/@content")[0]
)

singleUsp = all_data.get('akeneoProductData', {}).get('singleUsp', "")

# ---------------- DIMENSIONS ----------------

dim = all_data.get('articleData', {}).get('dimensions', {})

dimensions_obj = Dimensions(
    d1=dim.get('d1', 0),
    d2=dim.get('d2', 0),
    b1=dim.get('b1', 0)
)

# ---------------- MANUFACTURING ----------------

manufacturing_method = all_data.get('_nextI18Next', {}) \
    .get('userConfig', {}) \
    .get('resources', {}) \
    .get('en', {}) \
    .get('bearing-hub/bearingHub', {}) \
    .get('PRODUCTION_METHODS', {}) \
    .get('MOLD_INJECTION', "")

# ---------------- MATERIAL PROPERTIES ----------------

attribute = []
material_html = all_data.get('akeneoProductData', {}) \
    .get('attributes', {}) \
    .get('attr_USP', {}) \
    .get('value', "")

if material_html:
    try:
        pro = html.fromstring(material_html)
    except:
        pro = html.fromstring(f"<div>{material_html}</div>")

    items = pro.xpath("//li/text()")
    attribute = [i.strip() for i in items if i.strip()]

# ---------------- PRICING ----------------

article = all_data.get('articleData', {})

qty = article.get('quantity', 0)
unit = article.get('unitPriceForOne', {}).get('unit', "")

totalprice = article.get('totalPrice', {}).get('value', 0)
unitprice = article.get('unitPrice', {}).get('value', 0)
setupcost = article.get('setupCost', {}).get('value', 0)

# ---------------- PRODUCT DESCRIPTION ----------------

pro_desc = {}

desc_html = all_data.get('akeneoProductData', {}) \
    .get('attributes', {}) \
    .get('attr_description', {}) \
    .get('value', "")

if desc_html:
    try:
        desc_tree = html.fromstring(desc_html)
    except:
        desc_tree = html.fromstring(f"<div>{desc_html}</div>")

    keys = desc_tree.xpath("//b/text()")
    values = desc_tree.xpath("//b/parent::*//text()")

    for i in range(len(keys)):
        key = keys[i].strip()
        value = "".join(values).replace(key, "").strip()
        pro_desc[key] = value

# ---------------- TECHNICAL DATA ----------------

technical_data_list = []

tech_data = all_data.get('technicalDataCategories', [])

for cat in tech_data:
    attributes = []

    for att in cat.get('attributes', []):
        attributes.append(
            Technical_Attribues(
                description=att.get('description', ""),
                value=att.get('value', ""),
                icon=att.get('icon')
            )
        )

    technical_data_list.append(
        Technical_Data(
            name=cat.get('name', ""),
            label=cat.get('label', ""),
            attributes=attributes
        )
    )

# ---------------- FINAL OBJECT ----------------

query_obj = Query(
    partno=partno,
    categoryName=category,
    shape=shape
)

product = Product(
    title=title,
    query=query_obj,
    img=img_url,
    singleUsp=singleUsp,
    dimensions=dimensions_obj,
    manufacturing_method=manufacturing_method,
    material_properties=attribute,
    quantity=qty,
    unit=unit,
    totalPrice=totalprice,
    unitPrice=unitprice,
    setupCost=setupcost,
    product_description=pro_desc,
    technical_data=technical_data_list
)

# ---------------- SAVE JSON ----------------

with open("igus_output.json", "w", encoding="utf-8") as f:
    json.dump(product.model_dump(), f, indent=4, ensure_ascii=False)

print("✅ IGUS output file created successfully")