import json

with open("flipkart/sample.json","r") as f:
    data=json.load(f)

page=data.get("RESPONSE",{}).get("pageData",{})
context=page.get("pageContext",{})
seo=page.get("seoData",{}).get("seo",{})
tracking = context.get("trackingDataV2", {})

product={
    "product_id":context.get("productId"),
    "product_name":None,
    "product_url":seo.get("canonical"),
    "brand":None,
    "price":None,
    "rating":None,
    "review":None,
    "availability":{
        "cod_available":tracking.get("codAvailable"),
        "delivery_available":tracking.get("serviceable")
    },
    "seller_info":{
        "seller_name":None,
        "seller_rating":context.get("trackingDataV2").get("sellerRating")
    },
    "product_media":{
        "images":[]
    },
    "product_details":{
        "description":seo.get("description"),
        
    }
}


title=seo.get("title")

if title:
    product["product_name"]=title.split("price")[0]

if product["product_name"]:
    words=product["product_name"].split()
    if len(words) > 0:
        product["brand"]=words[0]


image=seo.get("ogImage")
if image:
    image=image.replace("{@width}","500").replace("{@height}","500")
    product["product_media"]["images"].append(image)

with open("flipkart/flipkart_output.json","w") as f:
    json.dump(product,f,indent=4)

print("Flipkart Json Created")