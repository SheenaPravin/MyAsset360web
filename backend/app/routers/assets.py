from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.family import resolve_family_id
from app.core.security import get_current_user
from app.models.models import Asset, Liability, User
from app.schemas import schemas

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("/summary/net-worth")
def net_worth_summary(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    aq = db.query(func.coalesce(func.sum(Asset.current_value), 0.0))
    lq = db.query(func.coalesce(func.sum(Liability.outstanding), 0.0))
    if family_id is not None:
        aq = aq.filter(Asset.family_id == family_id)
        lq = lq.filter(Liability.family_id == family_id)
    total_assets = float(aq.scalar() or 0.0)
    total_liabilities = float(lq.scalar() or 0.0)
    return {
        "family_id": family_id,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities,
    }


@router.get("/", response_model=list[schemas.AssetOut])
def list_assets(
    asset_type: str | None = Query(default=None),
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Asset)
    if asset_type:
        q = q.filter(Asset.asset_type == asset_type)
    if family_id is not None:
        q = q.filter(Asset.family_id == family_id)
    return q.order_by(Asset.id.desc()).all()


@router.post("/", response_model=schemas.AssetOut)
def create_asset(
    payload: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data["family_id"] = resolve_family_id(db, current_user, payload.family_id)
    asset = Asset(**data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=schemas.AssetOut)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=schemas.AssetOut)
def update_asset(
    asset_id: int,
    payload: schemas.AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"ok": True}
