from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Family, FamilyMember, User
from app.schemas import schemas

router = APIRouter(prefix="/api/families", tags=["families"])


def _get_family_or_404(db: Session, family_id: int) -> Family:
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family


@router.get("/", response_model=list[schemas.FamilyOut])
def list_families(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Family).filter(Family.owner_id == current_user.id).all()


@router.post("/", response_model=schemas.FamilyOut)
def create_family(
    payload: schemas.FamilyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    family = Family(name=payload.name, owner_id=current_user.id)
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


@router.get("/{family_id}", response_model=schemas.FamilyOut)
def get_family(
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_family_or_404(db, family_id)


@router.put("/{family_id}", response_model=schemas.FamilyOut)
def update_family(
    family_id: int,
    payload: schemas.FamilyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    family = _get_family_or_404(db, family_id)
    if payload.name is not None:
        family.name = payload.name
    db.commit()
    db.refresh(family)
    return family


@router.delete("/{family_id}")
def delete_family(
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    family = _get_family_or_404(db, family_id)
    db.delete(family)
    db.commit()
    return {"ok": True}


# ---------- Members ----------
@router.get("/{family_id}/members", response_model=list[schemas.FamilyMemberOut])
def list_members(
    family_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_family_or_404(db, family_id)
    return db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()


@router.post("/{family_id}/members", response_model=schemas.FamilyMemberOut)
def create_member(
    family_id: int,
    payload: schemas.FamilyMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_family_or_404(db, family_id)
    member = FamilyMember(family_id=family_id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/members/{member_id}", response_model=schemas.FamilyMemberOut)
def update_member(
    member_id: int,
    payload: schemas.FamilyMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(member, k, v)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/members/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return {"ok": True}
