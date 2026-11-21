from datetime import datetime, timedelta
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..config import settings
from ..database import get_db
from ..models import MonitoringLocation, AirQualityReading, Pollutant, PollutantValue, SavedLocation, User
from ..security import get_current_user

router = APIRouter(prefix="/readings", tags=["Air Quality"])

POLLUTANTS = {
    "pm2_5": ("PM2.5", "µg/m³"), "pm10": ("PM10", "µg/m³"),
    "carbon_monoxide": ("Carbon Monoxide", "µg/m³"),
    "nitrogen_dioxide": ("Nitrogen Dioxide", "µg/m³"),
    "sulphur_dioxide": ("Sulphur Dioxide", "µg/m³"),
    "ozone": ("Ozone", "µg/m³")
}

async def fetch_open_meteo(lat: float, lon: float, timezone: str = "auto"):
    params = {"latitude": lat, "longitude": lon, "hourly": ",".join(POLLUTANTS.keys()),
              "current": ",".join(POLLUTANTS.keys()), "timezone": timezone, "forecast_days": 1}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(settings.open_meteo_base_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        raise HTTPException(502, "Open-Meteo could not be reached. Please try again.")

def ensure_pollutants(db: Session):
    for code, (name, unit) in POLLUTANTS.items():
        if not db.query(Pollutant).filter_by(code=code).first():
            db.add(Pollutant(code=code, name=name, unit=unit))
    db.flush()

@router.post("/refresh/{location_id}")
async def refresh(location_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    saved = db.query(SavedLocation).filter_by(user_id=user.id, location_id=location_id).first()
    if not saved: raise HTTPException(403, "Save this city to your account before refreshing it.")
    location = db.get(MonitoringLocation, location_id)
    if not location: raise HTTPException(404, "Monitoring location not found.")
    payload = await fetch_open_meteo(location.latitude, location.longitude, location.city.timezone or "auto")
    current = payload.get("current") or {}
    timestamp = current.get("time")
    if not timestamp:
        raise HTTPException(502, "The data provider did not return a current timestamp.")
    recorded_at = datetime.fromisoformat(timestamp)
    ensure_pollutants(db)
    reading = AirQualityReading(location_id=location.id, recorded_at=recorded_at, source="Open-Meteo")
    db.add(reading); db.flush()
    values = []
    for code in POLLUTANTS:
        value = current.get(code)
        if value is None: continue
        pollutant = db.query(Pollutant).filter_by(code=code).first()
        db.add(PollutantValue(reading_id=reading.id, pollutant_id=pollutant.id, value=float(value)))
        values.append({"code": code, "name": POLLUTANTS[code][0], "unit": POLLUTANTS[code][1], "value": float(value)})
    db.commit()
    return {"reading_id": reading.id, "recorded_at": recorded_at.isoformat(), "source": "Open-Meteo", "values": values}

@router.get("/latest/{location_id}")
def latest(location_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(SavedLocation).filter_by(user_id=user.id, location_id=location_id).first():
        raise HTTPException(403, "This location is not saved to your account.")
    reading = db.query(AirQualityReading).filter_by(location_id=location_id).order_by(AirQualityReading.recorded_at.desc()).first()
    if not reading: return {"reading": None, "message": "No readings yet. Use Refresh data to fetch the latest measurements."}
    return {"reading": serialize_reading(reading)}

def serialize_reading(reading):
    return {"id": reading.id, "recorded_at": reading.recorded_at.isoformat(), "source": reading.source,
            "values": [{"code": v.pollutant.code, "name": v.pollutant.name, "unit": v.pollutant.unit, "value": v.value} for v in reading.values]}

@router.get("/history/{location_id}")
def history(location_id: int, days: int = Query(default=7, ge=1, le=90), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(SavedLocation).filter_by(user_id=user.id, location_id=location_id).first():
        raise HTTPException(403, "This location is not saved to your account.")
    since = datetime.utcnow() - timedelta(days=days)
    rows = db.query(AirQualityReading).filter(AirQualityReading.location_id == location_id, AirQualityReading.recorded_at >= since).order_by(AirQualityReading.recorded_at.asc()).all()
    return [serialize_reading(r) for r in rows]

@router.get("/analytics/{location_id}")
def analytics(location_id: int, days: int = Query(default=7, ge=1, le=90), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.query(SavedLocation).filter_by(user_id=user.id, location_id=location_id).first():
        raise HTTPException(403, "This location is not saved to your account.")
    since = datetime.utcnow() - timedelta(days=days)
    rows = (db.query(Pollutant.code, Pollutant.name, Pollutant.unit, func.avg(PollutantValue.value), func.max(PollutantValue.value))
            .join(PollutantValue, Pollutant.id == PollutantValue.pollutant_id)
            .join(AirQualityReading, AirQualityReading.id == PollutantValue.reading_id)
            .filter(AirQualityReading.location_id == location_id, AirQualityReading.recorded_at >= since)
            .group_by(Pollutant.id, Pollutant.code, Pollutant.name, Pollutant.unit).all())
    return {"days": days, "metrics": [{"code": r[0], "name": r[1], "unit": r[2], "average": round(float(r[3]), 2), "maximum": round(float(r[4]), 2)} for r in rows]}


@router.get("/compare")
def compare_saved_cities(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Compare the latest stored measurements across the user's saved locations."""
    saved_rows = db.query(SavedLocation).filter_by(user_id=user.id).all()
    results = []
    for saved in saved_rows:
        location = saved.location
        reading = (db.query(AirQualityReading)
                   .filter_by(location_id=location.id)
                   .order_by(AirQualityReading.recorded_at.desc()).first())
        values = {}
        if reading:
            for item in reading.values:
                values[item.pollutant.code] = item.value
        results.append({
            "location_id": location.id,
            "city": location.city.name,
            "country": location.city.country,
            "recorded_at": reading.recorded_at.isoformat() if reading else None,
            "values": values
        })
    return {"locations": results, "note": "Comparison uses each location's latest stored reading; refresh locations to update the comparison."}
