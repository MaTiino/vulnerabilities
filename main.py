from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal, Base, engine
from models import Advisory, Device, DeviceGroup, Notification
from scheduler import start_scheduler
from match_engine import match_advisories_to_devices
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app once
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    start_scheduler()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class DeviceInput(BaseModel):
    model: str
    os_version: str = ""
    hostname: str = ""
    serial_number: str = ""
    group_id: Optional[int] = None

class DeviceGroupInput(BaseModel):
    name: str

# Device endpoints
@app.post("/devices/", response_model=dict)
def add_device(device: DeviceInput, db: Session = Depends(get_db)):
    db_device = Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return {"id": db_device.id, "model": db_device.model}

@app.get("/devices/", response_model=List[dict])
def list_devices(db: Session = Depends(get_db)):
    return [
        {
            "id": d.id,
            "model": d.model,
            "hostname": d.hostname,
            "serial_number": d.serial_number,
            "os_version": d.os_version,
            "group_id": d.group_id
        } for d in db.query(Device).all()
    ]

@app.get("/devices/{device_id}", response_model=dict)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "id": device.id,
        "model": device.model,
        "hostname": device.hostname,
        "serial_number": device.serial_number,
        "os_version": device.os_version,
        "group_id": device.group_id
    }

@app.put("/devices/{device_id}", response_model=dict)
def update_device(device_id: int, device: DeviceInput, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in device.dict().items():
        setattr(db_device, key, value)
    db.commit()
    db.refresh(db_device)
    return {"message": "Device updated successfully"}

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}

# Group endpoints
@app.post("/groups/", response_model=dict)
def create_group(group: DeviceGroupInput, db: Session = Depends(get_db)):
    db_group = DeviceGroup(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return {"id": db_group.id, "name": db_group.name}

@app.get("/groups/", response_model=List[dict])
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(DeviceGroup).all()
    return [{"id": g.id, "name": g.name, "device_count": len(g.devices)} for g in groups]

# Advisory endpoints
@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    advisories = db.query(Advisory).order_by(Advisory.publication_date.desc()).all()
    return [
        {
            "advisory_id": a.advisory_id,
            "title": a.title,
            "severity": a.severity,
            "publication_date": a.publication_date.isoformat(),
            "product": a.product
        } for a in advisories
    ]

@app.get("/alerts/match")
def match_alerts(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    device_data = [{"id": d.id, "model": d.model} for d in devices]
    return match_advisories_to_devices(db, device_data)

@app.get("/alerts/match/group/{group_id}")
def match_alerts_by_group(group_id: int, db: Session = Depends(get_db)):
    devices = db.query(Device).filter(Device.group_id == group_id).all()
    device_data = [{"id": d.id, "model": d.model} for d in devices]
    return match_advisories_to_devices(db, device_data)