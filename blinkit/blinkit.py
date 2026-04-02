import json

with open("blinkit/blinkit.json", "r") as f:
    data = json.load(f)

widgets = data.get("response", {}).get("snippets", [])

product = {}
price_variations = []
images = []
video_url = None
attributes = {}

response_tracking = data.get("response", {}).get("tracking", {})
le_meta = response_tracking.get("le_meta", {})
if le_meta:
    custom_data = le_meta.get("custom_data", {})
    if custom_data:
        seo = custom_data.get("seo", {})
        if seo and "attributes" in seo:
            seo_attributes = seo["attributes"]
            for attr in seo_attributes:
                attr_name = attr.get("name")
                attr_value = attr.get("value")
                if attr_name and attr_value:
                    attributes[attr_name] = attr_value

for widget in widgets:
    widget_type = widget.get("widget_type")

    if widget_type == "text_right_icons_rating_snippet_type":
        d = widget.get("data", {})
        tracking = widget.get("tracking", {}).get("common_attributes", {})

        product["name"] = d.get("title", {}).get("text")
        product["brand"] = "4700BC"
        product["price"] = tracking.get("price")
        product["weight"] = attributes.get("Unit", "55 g")  
        product["currency"] = tracking.get("currency", "INR")

    if widget_type == "carousal_list_vr":
        items = widget.get("data", {}).get("itemList", [])
        for item in items:
            media = item.get("data", {}).get("media_content", {})
            if media.get("media_type") == "image":
                images.append(media.get("image", {}).get("url"))
            elif media.get("media_type") == "video":
                video_url = media.get("video", {}).get("url")

    if widget_type == "horizontal_list":
        items = widget.get("data", {}).get("horizontal_item_list", [])
        
        if items and items[0].get("tracking", {}).get("impression_map", {}).get("event_name") == "Product Variant Shown":
            base_name = product.get("name", "")
            for item in items:
                d = item.get("data", {})
                impression = item.get("tracking", {}).get("impression_map", {})

                variant_text = d.get("title", {}).get("text", "")
              
                if variant_text == "55 g":
                    variant_name = base_name
                elif variant_text == "2 x 55 g":
                    variant_name = f"{base_name.replace('Corn Chips+', 'Corn Popped Chips +')} - Pack of 2"
                elif variant_text == "3 x 55 g":
                    variant_name = f"{base_name.replace('Corn Chips+', 'Corn Popped Chips +')} - Pack of 3"
                else:
                    variant_name = f"{base_name} - {variant_text}"

                variation = {
                    "name": variant_name,
                    "weight": variant_text,
                    "price": impression.get("price"),
                    "is_selected": d.get("selection_config", {}).get("is_selected", False),
                }
                price_variations.append(variation)

output = {
    "name": product.get("name"),
    "brand": product.get("brand"),
    "price": product.get("price"),
    "weight": product.get("weight"),
    "currency": product.get("currency"),
    "product_varient": price_variations,
    "Gallary": {
        "video": [video_url] if video_url else [],
        "images": images
    },
    "attributes": attributes
}

with open("blinkit/blinkit_output.json", "w") as f:
    json.dump(output, f, indent=4)

print("Blinkit JSON output file created successfully.")