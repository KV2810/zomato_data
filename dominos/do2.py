import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.dominos.co.in"

# ✅ Headers (important to avoid blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.dominos.co.in/"
}


# ✅ Step 1: Get all city links
def get_city_links():
    url = BASE_URL + "/store-location"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        print("❌ Failed to fetch city list")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    city_links = []

    for a in soup.select(".citylist-ul li a"):
        city_name = a.text.strip()
        city_url = BASE_URL + a["href"]

        city_links.append({
            "city": city_name,
            "url": city_url
        })

    print(f"✅ Found {len(city_links)} cities")
    return city_links


# ✅ Step 2: Get stores using API
def get_stores_from_city(city):
    city_name = city["city"].split("(")[0].strip()

    print(f"📍 Scraping: {city_name}")

    url = "https://www.dominos.co.in/store-location/getStoreByCity"

    try:
        res = requests.post(url, data={"city": city_name}, headers=HEADERS)

        if res.status_code != 200:
            print(f"❌ Failed request for {city_name}")
            return []

        data = res.json()

    except Exception as e:
        print(f"❌ Error for {city_name}: {e}")
        return []

    stores = []

    for store in data.get("stores", []):
        stores.append({
            "city": city_name,
            "store_name": store.get("storeName"),
            "address": store.get("address"),
            "phone": store.get("phone"),
            "latitude": store.get("latitude"),
            "longitude": store.get("longitude"),
        })

    print(f"   ➤ Found {len(stores)} stores")
    return stores


# ✅ Step 3: Main function
def main():
    all_data = []

    # create folder if not exists
    os.makedirs("dominos", exist_ok=True)

    cities = get_city_links()

    for city in cities:
        stores = get_stores_from_city(city)
        all_data.extend(stores)

        time.sleep(0.5)  # prevent blocking

    # ✅ Save JSON
    with open("dominos/dominos_stores1.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print("\n🎉 Done! Data saved to dominos/dominos_stores.json")
    print(f"📦 Total stores collected: {len(all_data)}")


# ✅ Run
if __name__ == "__main__":
    main()