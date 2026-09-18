from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.family import resolve_family_id
from app.core.security import get_current_user
from app.models.models import InsurancePolicy, User
from app.schemas import schemas

router = APIRouter(prefix="/api/insurance", tags=["insurance"])


@router.get("/", response_model=list[schemas.InsuranceOut])
def list_policies(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(InsurancePolicy)
    if family_id is not None:
        q = q.filter(InsurancePolicy.family_id == family_id)
    return q.order_by(InsurancePolicy.id.desc()).all()


@router.post("/", response_model=schemas.InsuranceOut)
def create_policy(
    payload: schemas.InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data["family_id"] = resolve_family_id(db, current_user, payload.family_id)
    policy = InsurancePolicy(**data)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/{policy_id}", response_model=schemas.InsuranceOut)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=schemas.InsuranceOut)
def update_policy(
    policy_id: int,
    payload: schemas.InsuranceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(policy, k, v)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"ok": True}
