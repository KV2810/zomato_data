import json
from pydantic import BaseModel
from typing import List, Optional

class Image(BaseModel):
    id: str
    url: str
    label: Optional[str]

class Price(BaseModel):
    discounted: Optional[str]
    original: Optional[str]
    currency: str
    qualifier: Optional[str]

class Policy(BaseModel):
    check_in: Optional[str]=None
    check_out: Optional[str]=None
    max_guests: Optional[int]=None
    pets_allowed: Optional[bool]=None
    cancellation: Optional[str]=None

class Review(BaseModel):
    reviewer: str
    rating: int
    comment: str
    date: str

class Listing(BaseModel):
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]=None
    capacity: Optional[int]
    property_type: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]

    images: List[Image]
    price: Optional[Price]
    policies: Optional[Policy]
    reviews: List[Review]

with open("airbnb/air_bnb.json","r",encoding="utf-8") as f:
    raw=json.load(f)

with open("airbnb/air_bnb2.json","r",encoding="utf-8") as f:
    raw11=json.load(f)

with open("airbnb/airbnb_review.json","r",encoding="utf-8") as f:
    raw2=json.load(f)

sections = raw["niobeClientData"][0][1]["data"]["presentation"]["stayProductDetailPage"]["sections"]["sections"]
description=None
images=[]
meta={}

for sec in sections:
    section=sec.get("section") or {}

    for img in section.get("images",[]):
        images.append(Image(id=img.get("id",""),url=img.get("url",""),label=img.get("accessibilityLabel")))

    if "shareSave" in section:
        embed = section["shareSave"]["embedData"]

        meta = {
            "title": embed.get("name"),
            "capacity": embed.get("personCapacity"),
            "property_type": embed.get("propertyType"),
            "rating": embed.get("starRating"),
            "review_count": embed.get("reviewCount"),
        }


# ---------------- EXTRACT FROM FILE 2 ----------------
sections2 = raw11["data"]["presentation"]["stayProductDetailPage"]["sections"]["sections"]

price_obj = None
policy_obj = Policy()

for sec in sections2:
    section = sec.get("section") or {}

    # Price
    if "structuredDisplayPrice" in section:
        p = section["structuredDisplayPrice"]["primaryLine"]

        price_obj = Price(
            discounted=p.get("discountedPrice"),
            original=p.get("originalPrice"),
            currency="INR",
            qualifier=p.get("qualifier")
        )

    # Policies
    if sec.get("sectionId") == "POLICIES_DEFAULT":

        for rule in section.get("houseRules", []):
            text = rule["title"]

            if "Check-in" in text:
                policy_obj.check_in = text
            elif "Checkout" in text:
                policy_obj.check_out = text
            elif "guests" in text:
                policy_obj.max_guests = int(text.split()[0])

        for grp in section.get("houseRulesSections", []):
            for item in grp.get("items", []):
                if "Pets allowed" in item["title"]:
                    policy_obj.pets_allowed = True

        cancellation = section["cancellationPolicyForDisplay"]["subtitles"]
        policy_obj.cancellation = " ".join(cancellation)

reviews_raw = raw2["data"]["presentation"]["stayProductDetailPage"]["reviews"]["reviews"]

reviews = []
for r in reviews_raw:
    reviews.append(Review(
        reviewer=r["reviewer"]["firstName"],
        rating=r["rating"],
        comment=r["comments"],
        date=r["localizedDate"]
    ))

listing = Listing(
    title=meta.get("title"),
    description=description,
    capacity=meta.get("capacity"),
    property_type=meta.get("property_type"),
    rating=meta.get("rating"),
    review_count=meta.get("review_count"),
    images=images,
    price=price_obj,
    policies=policy_obj,
    reviews=reviews
)

with open("airbnb/airbnb_output.json","w",encoding="utf-8") as f:
    json.dump(listing.model_dump(),f,indent=4)