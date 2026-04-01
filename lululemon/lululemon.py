import json

with open("lululemon/lululemon.json","r") as f:
    raw=json.load(f)

product_data= raw.get("data", {}).get("itemToItems", {}).get("products", [])

BASE_URL = "https://shop.lululemon.com"

products = []

for item in product_data:
    product={
        "id":item.get("id"),
        "sku_id": item.get("skuId"),
        "product_id": item.get("productId"),
        "display_name":item.get("displayName"),
        "productOnSale":item.get("productOnSale"),
        "price": float(item.get("listPrice")[0]) if item.get("listPrice") else None,
        "sale_price": float(item.get("salePrice")[0]) if item.get("salePrice") else None,
        "product_url":item.get("pdpUrl"),
        "product_media": {
            "images": item.get("skuImages", [])
        },
        "variants":[]
    }

    pdp = item.get("pdpUrl")
    if pdp:
        product["product_url"] = BASE_URL + pdp

    for var in item.get("skuStyleOrder", []):
        variant = {
            "id": var.get("id"),
            "sku_style_order_id": var.get("skuStyleOrderId"),
            "color_id": var.get("colorId"),
            "style_id": var.get("styleId"),
            "style_id_01": var.get("styleId01"),
            "style_id_02": var.get("styleId02"),
            "color_name": var.get("colorName"),
            "color_group": var.get("colorGroup", [])
        }

        product["variants"].append(variant)

    products.append(product)

with open("lululemon/lululemon_output.json","w") as f:
    json.dump(products,f,indent=4)

print("lululemon json output file is created")