import json

# Load JSON file
with open("flipkart/sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Navigate JSON safely
page = data.get("RESPONSE", {}).get("pageData", {})
context = page.get("pageContext", {})
seo = page.get("seoData", {}).get("seo", {})
tracking = context.get("trackingDataV2", {})

# Initialize product structure
product = {
    "product_id": context.get("productId"),
    "product_name": None,
    "product_url": seo.get("canonical"),
    "brand": None,
    "price": None,
    "rating": None,
    "review": None,
    "availability": {
        "cod_available": tracking.get("codAvailable"),
        "delivery_available": tracking.get("serviceable")
    },
    "seller_info": {
        "seller_name": None,
        "seller_rating": tracking.get("sellerRating")
    },
    "product_media": {
        "images": []
    },
    "product_details": {
        "description": seo.get("description")
    }
}

# Extract product name & brand safely
title = seo.get("title")

if title and "{TITLE}" not in title:
    name = title.split("Price")[0].strip()
    product["product_name"] = name

    words = name.split()
    if words:
        product["brand"] = words[0]

# Extract image and clean placeholders
image = seo.get("ogImage")
if image:
    image = image.replace("{@width}", "500").replace("{@height}", "500")
    product["product_media"]["images"].append(image)

# Save output JSON
with open("flipkart/flipkart_output1.json", "w", encoding="utf-8") as f:
    json.dump(product, f, indent=4)

print("Flipkart JSON Created Successfully")