from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from db import get_db
from models import Device, DeviceGroup

router = APIRouter()

@router.get("/rack-view")
def get_rack_view(db: Session = Depends(get_db)):
    # This would return data for frontend visualization
    groups = db.query(DeviceGroup).all()
    
    rack_data = []
    for group in groups:
        devices = []
        for device in group.devices:
            # Get matched advisories for each device
            advisories = match_advisories_to_devices(db, [{"model": device.model, "id": device.id}])
            devices.append({
                "id": device.id,
                "model": device.model,
                "hostname": device.hostname,
                "advisory_count": len(advisories),
                "critical_advisories": sum(1 for a in advisories if a["advisory"]["severity"].lower() == "critical")
            })
        
        rack_data.append({
            "group_id": group.id,
            "group_name": group.name,
            "devices": devices
        })
    
    return {"racks": rack_data}