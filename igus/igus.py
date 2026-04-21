import json
from pydantic import BaseModel,RootModel
from typing import List,Optional,Union,Dict
from lxml import html

class Query(BaseModel):
    partno:str
    categoryName:str
    shape:str

class Dimensions(BaseModel):
    d1:int
    d2:int
    b1:int

class Technical_Attribues(BaseModel):
    description:str
    value:Union[str,bool]

class Technical_Data(BaseModel):
    name:str
    attributes:List[Technical_Attribues]

class Product(BaseModel):
    title:str
    query:Query
    img:List[str]=None
    singleUsp:str
    dimensions:Dimensions
    manufacturing_method:str
    material_properties:List[str]
    quantity:int
    unit:str
    totalPrice:float=0
    unitPrice:float=0
    setupCost:float=0
    product_description:Dict[str,str]
    technical_data:List[Technical_Data]

with open("igus/igus.html","r",encoding="utf-8") as f:
    data=f.read()

tree=html.fromstring(data)
script="".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
data2=json.loads(script)
all_data=data2.get('props').get('pageProps')
query=data2.get('query')

attribute=[]
pro_desc={}


title=all_data.get('akeneoProductData').get('title')
print(title)
partno = query.get('artnr')
print(partno)
shape=query.get('shape')
print(shape)
category=query.get('categoryName')
print(category)
img = tree.xpath("//div[contains(@class,'grid grid-cols-1')]/div//noscript//img/@src")
img=list(set(img))
print(img)
singleUsp=all_data.get('akeneoProductData').get('singleUsp')
print(singleUsp)
dimensions=all_data.get('articleData').get('dimensions')
print(dimensions)
manufacturing_method=all_data.get('_nextI18Next').get('userConfig').get('resources').get('en').get('bearing-hub/bearingHub').get('PRODUCTION_METHODS').get('MOLD_INJECTION')
print(manufacturing_method)
material_properties=all_data.get('akeneoProductData').get('attributes').get('attr_USP').get('value')
print(material_properties)
pro=html.fromstring(material_properties)
p=pro.xpath("li/text()")
for p in p:
    attribute.append(p)
print(attribute)
article = all_data.get('articleData', {})

qty = article.get('quantity', 0)
print(qty)
unit = article.get('unitPriceForOne', {}).get('unit', "")
print(unit)
totalprice = article.get('totalPrice', {}).get('value', 0)
print(totalprice)
unitprice = article.get('unitPrice', {}).get('value', 0)
print(unitprice)
setupcost = article.get('setupCost', {}).get('value', 0)
print(setupcost)

product_description=all_data.get('akeneoProductData',{}).get('attributes',{}).get('attr_description',{}).get('value',"")
attr_desc=html.fromstring(product_description)
a=attr_desc.xpath("b/text()")[0]
desc=attr_desc.xpath("//b[contains(text(),'iglidur® GLW')]/parent::*/text()")[0]
pro_desc[a]=desc
print(desc)
technical_data=[]
for i in all_data.get('technicalDataCategories',[]):
    technical_data.append(
        Technical_Data(
            name=i.get('name'),
            attributes=i.get('attributes')
        )
    )
print(technical_data)

query=Query(
    partno=partno,
    categoryName=category,
    shape=shape
)

output=Product(
    title=title,
    query=query,
    img=img,
    singleUsp=singleUsp,
    dimensions=dimensions,
    manufacturing_method=manufacturing_method,
    material_properties=attribute,
    quantity=qty,
    unit=unit,
    totalPrice=round(totalprice),
    unitPrice=unitprice,
    setupcost=setupcost,
    product_description=pro_desc,
    technical_data=technical_data
)

with open("igus/igus_output.json","w",encoding="utf-8") as f:
    json.dump(output.model_dump(),f,indent=4,ensure_ascii=False)

print("IGUS output file created successfully")
