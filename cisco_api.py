
import requests
import os
from datetime import datetime
from db import SessionLocal
from models import Advisory

def get_token():
    res = requests.post(os.getenv("CISCO_TOKEN_URL"), data={
        "grant_type": "client_credentials",
        "client_id": os.getenv("CISCO_CLIENT_ID"),
        "client_secret": os.getenv("CISCO_CLIENT_SECRET")
    })
    return res.json()["access_token"]

def fetch_advisories(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{os.getenv('CISCO_API_BASE')}/product", headers=headers)
    return res.json().get("advisories", [])

def fetch_and_store_advisories():
    token = get_token()
    advisories = fetch_advisories(token)
    db = SessionLocal()

    for adv in advisories:
        if not db.query(Advisory).filter_by(advisory_id=adv["advisoryId"]).first():
            db_adv = Advisory(
                advisory_id=adv["advisoryId"],
                title=adv.get("advisoryTitle", ""),
                severity=adv.get("sir", ""),
                publication_date=datetime.strptime(adv.get("firstPublished", "1970-01-01"), "%Y-%m-%dT%H:%M:%SZ").date(),
                product=", ".join([p["productName"] for p in adv.get("productNames", [])]),
                description=adv.get("advisorySummary", "")
            )
            db.add(db_adv)
    db.commit()
    db.close()
