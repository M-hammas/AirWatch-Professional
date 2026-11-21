from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert, User
from ..schemas import AlertIn, AlertOut
from ..security import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])
VALID_CODES = {"pm2_5", "pm10", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"}

@router.get("", response_model=list[AlertOut])
def list_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Alert).filter_by(user_id=user.id).order_by(Alert.id.desc()).all()

@router.post("", response_model=AlertOut, status_code=201)
def create_alert(data: AlertIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.pollutant_code not in VALID_CODES: raise HTTPException(422, "Unsupported pollutant code.")
    alert = Alert(user_id=user.id, pollutant_code=data.pollutant_code, threshold=data.threshold, enabled=int(data.enabled))
    db.add(alert); db.commit(); db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter_by(id=alert_id, user_id=user.id).first()
    if not alert: raise HTTPException(404, "Alert not found.")
    db.delete(alert); db.commit()
    return {"message": "Alert deleted."}
