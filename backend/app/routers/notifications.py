from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Notification, User
from app.schemas import schemas

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/upcoming", response_model=list[schemas.NotificationOut])
def upcoming_notifications(
    family_id: int | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(
        Notification.is_read.is_(False),
        (Notification.due_date.is_(None)) | (Notification.due_date >= date.today()),
    )
    if family_id is not None:
        q = q.filter(Notification.family_id == family_id)
    return q.order_by(Notification.due_date.asc().nullslast()).limit(limit).all()


@router.get("/", response_model=list[schemas.NotificationOut])
def list_notifications(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification)
    if family_id is not None:
        q = q.filter(Notification.family_id == family_id)
    return q.order_by(Notification.id.desc()).all()


@router.post("/", response_model=schemas.NotificationOut)
def create_notification(
    payload: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = Notification(**payload.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.get("/{notif_id}", response_model=schemas.NotificationOut)
def get_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.put("/{notif_id}", response_model=schemas.NotificationOut)
def update_notification(
    notif_id: int,
    payload: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(notif, k, v)
    db.commit()
    db.refresh(notif)
    return notif


@router.delete("/{notif_id}")
def delete_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"ok": True}
