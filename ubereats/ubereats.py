import json

with open("ubereats/ubereats1.json","r") as f:
    data=json.load(f)

basic=data.get("data",{})
location = basic.get("location", {})
store_meta = basic.get("storeInfoMetadata", {})
menu_data = basic.get("catalogSectionsMap", {})

restaurant={
    "title":basic.get("title"),
    "uuid":basic.get("uuid"),
    "slug":basic.get("slug"),
    "citySlug":basic.get("citySlug"),
    "heroImageUrls":[],
    "restaurant_contact": basic.get("phoneNumber"),
    "location":{
        "address":location.get("address"),
        "streetAddress":location.get("streetAddress"),
        "city":location.get("city"),
        "country":location.get("country"),
        "postalCode": location.get("postalCode"),
        "region": location.get("region"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude")
    },
    "cuisineList":basic.get("cuisineList",[]),
    "categories":basic.get("categories",[]),
    "priceBucket":basic.get("priceBucket"),
    "currencyCode":basic.get("currencyCode"),
    "timings":{},
    "delivery":{
        "isDeliveryThirdParty":basic.get("isDeliveryThirdParty"),
        "isDeliveryOverTheTop":basic.get("isDeliveryOverTheTop"),
        "isOrderable":basic.get("isOrderable"),
        "etaRange":basic.get("etaRange",{}).get("accessibilityText")
    },
    "menu_categories":[]
}

for image in basic.get( "heroImageUrls",[]):
    restaurant["heroImageUrls"].append({
        "url":image.get("url"),
        "width":image.get("width")
    })

for day_info in basic.get("hours",[]):
    day_range=day_info.get("dayRange","")
    sections = day_info.get("sectionHours", [])

    if sections:
        open_time = sections[0].get("startTime")
        close_time = sections[0].get("endTime")

        restaurant["timings"][day_range.lower()] = {
            "open": open_time,
            "close": close_time
        }
    

for section_id, sections in menu_data.items():
    for section in sections:
        payload = section.get("payload", {})
        items_data = payload.get("standardItemsPayload", {})

        category_name = items_data.get("title", {}).get("text")
        category_obj = {
            "category_name": category_name,
            "items": []
        }
        for item in items_data.get("catalogItems", []):
            category_obj["items"].append({
                "item_id": item.get("uuid"),
                "item_name": item.get("title"),
                "imageUrl":item.get("imageUrl"),
                "itemDescription":item.get("itemDescription"),
                "price":item.get("price"),
                "spanCount":item.get("spanCount"),
                "isAvailable":item.get("isAvailable"),
                "titleBadge":item.get("titleBadge",{}).get("text"),
                "itemDescriptionBadge":item.get("itemDescriptionBadge",{}).get("text")
            })

        restaurant["menu_categories"].append(category_obj)

with open("ubereats/ubereats_output.json", "w") as f:
    json.dump(restaurant, f, indent=4)

print("Clean Uber Eats JSON Created ")