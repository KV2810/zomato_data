import re
import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.dominos.co.in"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_city_links():
    url = BASE_URL + "/store-location"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    city_links = []

    for a in soup.select(".citylist-ul li a"):
        city_name = a.text.strip()
        city_url = BASE_URL + a["href"]
        city_links.append({
            "city": city_name,
            "url": city_url
        })

    return city_links

def get_stores_from_city(city):
    print(f"Scraping {city['city']}...")

    res = requests.get(city["url"], headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    stores = []

    cards = soup.select(".panel")  # store cards

    for card in cards:
        try:
            name_tag = card.select_one("h2.media-heading.city-main-title, .city-main-title")
            name = name_tag.text.strip() if name_tag else None

            subtitle_tag = card.select_one(".city-main-sub-title")
            address_tag = card.select_one("p.grey-text.mb-0")
            address_parts = []
            if subtitle_tag:
                address_parts.append(subtitle_tag.text.strip())
            if address_tag:
                address_parts.append(address_tag.text.strip())
            address = ", ".join(address_parts) if address_parts else None

            phone = None
            phone_match = re.search(r"Phone number\s*:\s*(\+?[\d\s-]+)", card.get_text(" ", strip=True))
            if phone_match:
                phone = phone_match.group(1).strip()

            # Extract delivery information
            card_text = card.get_text(" ", strip=True)
            
            delivery_time = None
            delivery_match = re.search(r"(\d+\s*mins?)\s*delivery", card_text, re.I)
            if delivery_match:
                delivery_time = delivery_match.group(1).strip()

            hours = None
            hours_match = re.search(r"Hours?:\s*([^|]+?)(?:\s*Open Now|\s*Closed|\s*Good for:)", card_text, re.I)
            if hours_match:
                hours = hours_match.group(1).strip()

            status = None
            status_match = re.search(r"(Open Now|Closed)", card_text, re.I)
            if status_match:
                status = status_match.group(1).strip()

            good_for = None
            good_for_match = re.search(r"Good for:\s*([^×\n]+?)(?:×|Domino)", card_text, re.I)
            if good_for_match:
                good_for = good_for_match.group(1).strip()

            stores.append({
                "city": city["city"],
                "store_name": name,
                "address": address,
                "phone": phone,
                "delivery_time": delivery_time,
                "hours": hours,
                "status": status,
                "good_for": good_for
            })

        except Exception as e:
            print("Error:", e)

    return stores


# Step 3: Run scraper
def main():
    all_data = []

    cities = get_city_links()

    for city in cities:
        stores = get_stores_from_city(city)
        all_data.extend(stores)

        time.sleep(1)  # avoid blocking

   
    with open("dominos/dominos_stores.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(" Done! Data saved to dominos_stores.json")


if __name__ == "__main__":
    main()