import json

with open("decathlon/decathlon.json", "r",encoding='utf-8') as f:
    raw = json.load(f)

state_data = json.loads(raw["props"]["initialState"])
product_page = state_data["reducer"]["productPage"]
active = product_page["activeProduct"]
description = active.get("description", {})
info = description.get("informationConcept", {})
price_data = active.get("priceForFront", {})
review = active.get("review", {})
seller = active.get('sellerDetail')


product={
    "product_id": active.get("modelId"),
    "product_name":description.get("productName"),
    "brand":active.get("brand"),
    "category": active.get("productCategory", {}).get("name"),
    "type": active.get("nature", {}).get("natureName"),
    "gender": info.get("gender"),
    "sport": info.get("sportPractice"),
    "stock": active.get("stockNotification", {}).get("message"),
    "seller_detailes": {
        'seller_name':seller.get('sellerName'),
        'address':seller.get('address'),
        'contact_no':seller.get('phone'),
        'email':seller.get('email')
    },
    "made_in":active.get("madeIn"),
    "description": description.get("descriptionShort"),
    "price":{
        "final_price": price_data.get("finalPrice"),
        "mrp": price_data.get("mrp"),
        "discount": price_data.get("mrp") - price_data.get("finalPrice") if price_data.get("mrp") else None
    },
    "rating": {
        "average": review.get("averageRating"),
        "count": review.get("count")
    },
    "images": [],
    "benefits": [],
    "product_specifications": [],
    "technical_information": [],
    "variants": [],
    "others": []
}

for img in active.get("images", []):
    product["images"].append(img.get("url"))

for b in description.get("benefits", []):
    name = b.get("name", "").title()
    desc = b.get("description", "").strip()

    if name and desc:
        product["benefits"].append(f"{name}: {desc}")


for spec in info.get("structuring", []):
    product["product_specifications"].append({
        "Key": spec.get("name").title(),
        "Value": spec.get("description")
    })

for tech in info.get("technicalInformation", []):
    product["technical_information"].append({
        "Key": tech.get("name"),
        "Value": tech.get("description", "").replace("\n", " ").strip()
    })

for art in active.get("articles", []):
    variation = {
        "articleId": art.get("articleId"),
        "size": art.get("attribute", {}).get("attributeValue"),
        "ean": art.get("ean"),
        "madeIn": art.get("madeIn"),
        "price": art.get("priceForFront", {}).get("finalPrice"),
        "mrp": art.get("priceForFront", {}).get("mrp"),
        "weight": art.get("weight", {}).get("weight"),
        "chest_size": None
    }

    size_info = art.get("sizeMeasurements", {})
    if size_info:
        variation["chest_size"] = f"{size_info.get('sizeMeasure')} {size_info.get('sizeFormat')}"

    product["variants"].append(variation)

for p in product_page.get("productsList", []):
    if p.get("modelId") == active.get("modelId"):
        continue

    desc = p.get("description", {})
    review = p.get("review", {})
    price = p.get("priceForFront", {})

    

    option = {
        "p_id": p.get("modelId"),
        "product_name": desc.get("productName"),
        "rating": review.get("averageRating"),
        "review_count": review.get("count"),
        "final_price": price.get("finalPrice"),
        "total_price": price.get("mrp"),
        "images": []
    }

    for img in p.get("images", []):
        option["images"].append(img.get("url"))

    product["others"].append(option)

with open("decathlon/decathlon_output.json", "w",encoding='utf-8') as f:
    json.dump(product, f, indent=4)

print("Decathlon JSON output file created successfully.")