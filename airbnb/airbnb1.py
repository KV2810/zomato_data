import json
from pydantic import BaseModel
from typing import List, Optional


# ---------------- SCHEMA ----------------
class Image(BaseModel):
    id: str
    url: str
    label: Optional[str] = None

class Price(BaseModel):
    discounted: Optional[str] = None
    original: Optional[str] = None
    currency: str = "INR"
    qualifier: Optional[str] = None

class Policy(BaseModel):
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    max_guests: Optional[int] = None
    pets_allowed: Optional[bool] = None
    cancellation: Optional[str] = None

class Review(BaseModel):
    reviewer: str
    rating: int
    comment: str
    date: str

class Host(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    id: Optional[str] = None
    image: Optional[str] = None
    is_superhost: Optional[bool] = None

class Listing(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    host: Optional[Host] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    property_type: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

    images: List[Image] = []
    price: Optional[Price] = None
    policies: Optional[Policy] = None
    reviews: List[Review] = []
    amenities: List[str] = [] 
    

with open("airbnb/air_bnb.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

with open("airbnb/air_bnb2.json", "r", encoding="utf-8") as f:
    raw11 = json.load(f)

with open("airbnb/airbnb_review.json", "r", encoding="utf-8") as f:
    raw2 = json.load(f)

query_str = raw["niobeClientData"][0][0]
query_params = json.loads(query_str.split(':', 1)[1].strip('"'))
date_range = query_params.get("dateRange", {})

sections = raw["niobeClientData"][0][1]["data"]["presentation"]["stayProductDetailPage"]["sections"]["sections"]

description = None
images = []
meta = {}
amenities = []

for sec in sections:
    section = sec.get("section") or {}

    if section.get("title") == "About this space":
        items = section.get("items", [])
        if items:
            description = items[0].get("html", {}).get("htmlText")


    media_items = section.get("mediaItems")

    if isinstance(media_items, list):
        for img in media_items:
            images.append(Image(
            id=img.get("id", ""),
            url=img.get("baseUrl", ""),
            label=img.get("accessibilityLabel")
        ))
 
    if "shareSave" in section:
        embed = section["shareSave"].get("embedData", {})

        meta = {
            "title": embed.get("name"),
            "capacity": embed.get("personCapacity"),
            "property_type": embed.get("propertyType"),
            "rating": embed.get("starRating"),
            "review_count": embed.get("reviewCount"),
        }

    if sec.get("sectionComponentType") == "AMENITIES_DEFAULT":
        for group in section.get("seeAllAmenitiesGroups", []):
            for item in group.get("amenities", []):
                amenities.append(item.get("title"))

meta["location"] = raw11.get("data", {}).get("presentation", {}).get("stayProductDetailPage", {}).get("sections", {}).get("metadata", {}).get("sharingConfig", {}).get("location")

sections2 = raw11["data"]["presentation"]["stayProductDetailPage"]["sections"]["sections"]

policy_data = {}

for sec in sections2:
    section = sec.get("section") or {}

    # Price
    if "structuredDisplayPrice" in section:
        p = section["structuredDisplayPrice"].get("primaryLine", {})

        price_obj = Price(
            discounted=p.get("discountedPrice"),
            original=p.get("originalPrice"),
            qualifier=p.get("qualifier")
        )

    # Policies
    if sec.get("sectionId") == "POLICIES_DEFAULT":

        for rule in section.get("houseRules", []):
            text = rule.get("title", "")

            if "Check-in" in text:
                policy_data["check_in"] = text
            elif "Checkout" in text:
                policy_data["check_out"] = text
            elif "guests" in text:
                try:
                    policy_data["max_guests"] = int(text.split()[0])
                except:
                    pass

        for grp in section.get("houseRulesSections", []):
            for item in grp.get("items", []):
                if "Pets allowed" in item.get("title", ""):
                    policy_data["pets_allowed"] = True

        cancellation = section.get("cancellationPolicyForDisplay", {}).get("subtitles", [])
        policy_data["cancellation"] = " ".join(cancellation)

# Add dates
policy_data["check_in_date"] = date_range.get("startDate")
policy_data["check_out_date"] = date_range.get("endDate")

policy_obj = Policy(**policy_data)

reviews_raw = raw2["data"]["presentation"]["stayProductDetailPage"]["reviews"]["reviews"]

reviews = []
for r in reviews_raw:
    reviews.append(Review(
        reviewer=r.get("reviewer", {}).get("firstName", ""),
        rating=r.get("rating", 0),
        comment=r.get("comments", ""),
        date=r.get("localizedDate", "")
    ))

host_data = None

reviews_list = raw2["data"]["presentation"]["stayProductDetailPage"]["reviews"]["reviews"]

if reviews_list:
    h = reviews_list[0].get("reviewee", {})

    host_data = Host(
        name=h.get("firstName"),
        hostname=h.get("hostName"),
        id=h.get("id"),
        image=h.get("pictureUrl"),
        is_superhost=h.get("isSuperhost")
    )

listing = Listing(
    title=meta.get("title"),
    description=description,
    location=meta.get("location"),
    capacity=meta.get("capacity"),
    property_type=meta.get("property_type"),
    rating=meta.get("rating"),
    review_count=meta.get("review_count"),
    images=images,
    price=price_obj,
    policies=policy_obj,
    reviews=reviews,
    host=host_data,
    amenities=amenities
)

with open("airbnb/airbnb_output1.json", "w", encoding="utf-8") as f:
    json.dump(listing.model_dump(), f, indent=4)

print("Data extracted successfully!")