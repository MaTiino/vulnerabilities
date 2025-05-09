from sqlalchemy.orm import Session
from models import Notification, Advisory, Device
from datetime import datetime

def check_for_new_advisories(db: Session):
    devices = db.query(Device).all()
    advisories = db.query(Advisory).all()
    
    for device in devices:
        for advisory in advisories:
            if device.model.lower() in advisory.product.lower():
                exists = db.query(Notification).filter(
                    Notification.device_id == device.id,
                    Notification.advisory_id == advisory.id
                ).first()
                
                if not exists:
                    notification = Notification(
                        device_id=device.id,
                        advisory_id=advisory.id
                    )
                    db.add(notification)
    db.commit()