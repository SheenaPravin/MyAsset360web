from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Liability, User
from app.schemas import schemas

router = APIRouter(prefix="/api/loans", tags=["loans"])


@router.get("/", response_model=list[schemas.LiabilityOut])
def list_loans(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Liability)
    if family_id is not None:
        q = q.filter(Liability.family_id == family_id)
    return q.order_by(Liability.id.desc()).all()


@router.post("/", response_model=schemas.LiabilityOut)
def create_loan(
    payload: schemas.LiabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = Liability(**payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("/{loan_id}", response_model=schemas.LiabilityOut)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = db.query(Liability).filter(Liability.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.put("/{loan_id}", response_model=schemas.LiabilityOut)
def update_loan(
    loan_id: int,
    payload: schemas.LiabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = db.query(Liability).filter(Liability.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(loan, k, v)
    db.commit()
    db.refresh(loan)
    return loan


@router.delete("/{loan_id}")
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = db.query(Liability).filter(Liability.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return {"ok": True}
