import json

with open('data.json','r') as file:
    data = json.load(file)

basic = data["page_data"]["sections"]["SECTION_BASIC_INFO"]
contact = data["page_data"]["sections"]["SECTION_RES_CONTACT"]
cuisine_data = data["page_data"]["sections"]["SECTION_RES_HEADER_DETAILS"]["CUISINES"]
menu_data = data["page_data"]["order"]["menuList"]["menus"]

restaurant={
    "restaurant_id":basic.get("res_id"),
    "restaurant_name":basic.get("name"),
    "restaurant_url":"https://www.zomato.com" + basic.get("resUrl",""),
    "restaurant_contact":[contact["phoneDetails"]["phoneStr"]],
    "fssai_licence_number": "",
    "address_info": {
        "full_address": contact.get("address"),
        "region": contact.get("locality_verbose"),
        "city": contact.get("city_name"),
        "pincode": int(contact.get("zipcode")),
        "state": "Gujarat"
    },
    "cuisines":[],
    "timings":{},
    "menu_categories":[]
}

for c in cuisine_data:
    restaurant["cuisines"].append(
        {
            "name": c.get("name"),
            "url": c.get("url")
        }
    )

timing_str=basic["timing"]["customised_timings"]["opening_hours"][0]["timing"]
   
parts=timing_str.split()

open_time=parts[0]
close_time=parts[-1]

for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]:
    restaurant["timings"][day]={
        "open":open_time.strip(),
        "close":close_time.strip()
    }
for menu in menu_data:
    category_name=menu["menu"]["name"]
    category_obj={
        "category_name":category_name,
        "items":[]
    }

    for cat in menu["menu"]["categories"]:
        for item_wrapper in cat["category"]["items"]:
            item=item_wrapper["item"]

            is_veg="non-veg" not in item.get("dietary_slugs",[])

            category_obj["items"].append(
                {
                    "item_id": item.get("id"), 
                    "item_name": item.get("name"),
                    "item_slugs": item.get("tag_slugs",[]),
                    "item_url": "",
                    "item_description": item.get("desc"),
                    "item_price": 0,
                    "is_veg": is_veg
                }
            )
    restaurant["menu_categories"].append(category_obj)

with open("data_output.json","w") as f:
    json.dump(restaurant,f,indent=4)

print("Clean Json Created")