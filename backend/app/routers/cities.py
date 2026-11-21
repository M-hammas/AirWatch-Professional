import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import City, MonitoringLocation, SavedLocation, User
from ..security import get_current_user

router = APIRouter(prefix="/cities", tags=["Cities"])

@router.get("/search")
async def search_cities(q: str = Query(min_length=2, max_length=100)):
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get(settings.geocoding_base_url, params={"name": q, "count": 8, "language": "en", "format": "json"})
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        raise HTTPException(502, "City search service is temporarily unavailable.")
    return {"results": [
        {"name": item.get("name"), "country": item.get("country", ""), "admin1": item.get("admin1", ""),
         "latitude": item["latitude"], "longitude": item["longitude"], "timezone": item.get("timezone", "UTC")}
        for item in payload.get("results", [])
    ]}

@router.post("/monitor")
async def monitor_city(data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    required = ["name", "latitude", "longitude"]
    if any(k not in data for k in required):
        raise HTTPException(422, "City name, latitude and longitude are required.")
    try:
        lat, lon = float(data["latitude"]), float(data["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(422, "Invalid coordinates.")
    name, country = str(data["name"])[:120], str(data.get("country", ""))[:120]
    city = db.query(City).filter(City.name == name, City.country == country, City.latitude == lat, City.longitude == lon).first()
    if not city:
        city = City(name=name, country=country, latitude=lat, longitude=lon, timezone=str(data.get("timezone", "UTC"))[:80])
        db.add(city); db.flush()
    location = db.query(MonitoringLocation).filter_by(city_id=city.id, latitude=lat, longitude=lon).first()
    if not location:
        location = MonitoringLocation(city_id=city.id, label="City centre", latitude=lat, longitude=lon)
        db.add(location); db.flush()
    saved = db.query(SavedLocation).filter_by(user_id=user.id, location_id=location.id).first()
    if not saved:
        db.add(SavedLocation(user_id=user.id, location_id=location.id))
    db.commit()
    return {"city_id": city.id, "location_id": location.id, "name": city.name, "country": city.country,
            "latitude": lat, "longitude": lon, "message": "Location saved. Fetch its latest air-quality reading from the dashboard."}

@router.get("/saved")
def saved_cities(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(SavedLocation).filter_by(user_id=user.id).all()
    result = []
    for row in rows:
        loc = row.location; city = loc.city
        result.append({"saved_id": row.id, "location_id": loc.id, "name": city.name, "country": city.country,
                       "latitude": loc.latitude, "longitude": loc.longitude})
    return result

@router.delete("/saved/{saved_id}")
def remove_saved(saved_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(SavedLocation).filter_by(id=saved_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Saved city not found.")
    db.delete(row); db.commit()
    return {"message": "Saved location removed."}
