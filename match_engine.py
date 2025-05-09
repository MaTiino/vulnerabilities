
from sqlalchemy.orm import Session
from models import Advisory

def match_advisories_to_devices(db: Session, devices: list):
    matched = []
    advisories = db.query(Advisory).all()
    
    for adv in advisories:
        affected_devices = []
        for device in devices:
            if (device["model"].lower() in adv.product.lower() or
                any(part.lower() in adv.product.lower() 
                    for part in device["model"].split())):
                
                affected_devices.append({
                    "model": device["model"],
                    "id": device.get("id")
                })
        
        if affected_devices:
            matched.append({
                "advisory": {
                    "id": adv.id,
                    "advisory_id": adv.advisory_id,
                    "title": adv.title,
                    "severity": adv.severity,
                    "publication_date": adv.publication_date.isoformat(),
                    "product": adv.product
                },
                "affected_devices": affected_devices
            })
    
    return matched