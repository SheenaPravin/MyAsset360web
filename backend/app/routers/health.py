from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.family import resolve_family_id, resolve_member_id
from app.core.security import get_current_user
from app.models.models import HealthcareExpense, HealthProfile, MedicalRecord, User
from app.schemas import schemas

router = APIRouter(prefix="/api/health", tags=["health"])


# ---------- Profiles ----------
@router.get("/profiles", response_model=list[schemas.HealthProfileOut])
def list_profiles(
    member_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(HealthProfile)
    if member_id is not None:
        q = q.filter(HealthProfile.member_id == member_id)
    return q.all()


@router.post("/profiles", response_model=schemas.HealthProfileOut)
def create_profile(
    payload: schemas.HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    family_id = resolve_family_id(db, current_user)
    member_id = resolve_member_id(db, current_user, family_id, payload.member_id)
    existing = (
        db.query(HealthProfile).filter(HealthProfile.member_id == member_id).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists for member")
    profile = HealthProfile(**{**payload.model_dump(), "member_id": member_id})
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profiles/{profile_id}", response_model=schemas.HealthProfileOut)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(HealthProfile).filter(HealthProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    return profile


@router.put("/profiles/{profile_id}", response_model=schemas.HealthProfileOut)
def update_profile(
    profile_id: int,
    payload: schemas.HealthProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(HealthProfile).filter(HealthProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/profiles/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(HealthProfile).filter(HealthProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    db.delete(profile)
    db.commit()
    return {"ok": True}


# ---------- Medical records ----------
@router.get("/records", response_model=list[schemas.MedicalRecordOut])
def list_records(
    member_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(MedicalRecord)
    if member_id is not None:
        q = q.filter(MedicalRecord.member_id == member_id)
    return q.order_by(MedicalRecord.id.desc()).all()


@router.post("/records", response_model=schemas.MedicalRecordOut)
def create_record(
    payload: schemas.MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    family_id = resolve_family_id(db, current_user)
    member_id = resolve_member_id(db, current_user, family_id, payload.member_id)
    record = MedicalRecord(**{**payload.model_dump(), "member_id": member_id})
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/records/{record_id}", response_model=schemas.MedicalRecordOut)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record


@router.put("/records/{record_id}", response_model=schemas.MedicalRecordOut)
def update_record(
    record_id: int,
    payload: schemas.MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    db.delete(record)
    db.commit()
    return {"ok": True}


# ---------- Expenses ----------
@router.get("/expenses", response_model=list[schemas.HealthcareExpenseOut])
def list_expenses(
    family_id: int | None = Query(default=None),
    member_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(HealthcareExpense)
    if family_id is not None:
        q = q.filter(HealthcareExpense.family_id == family_id)
    if member_id is not None:
        q = q.filter(HealthcareExpense.member_id == member_id)
    return q.order_by(HealthcareExpense.id.desc()).all()


@router.post("/expenses", response_model=schemas.HealthcareExpenseOut)
def create_expense(
    payload: schemas.HealthcareExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    data["family_id"] = resolve_family_id(db, current_user, payload.family_id)
    expense = HealthcareExpense(**data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses/{expense_id}", response_model=schemas.HealthcareExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(HealthcareExpense).filter(HealthcareExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/expenses/{expense_id}", response_model=schemas.HealthcareExpenseOut)
def update_expense(
    expense_id: int,
    payload: schemas.HealthcareExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(HealthcareExpense).filter(HealthcareExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(expense, k, v)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(HealthcareExpense).filter(HealthcareExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"ok": True}
