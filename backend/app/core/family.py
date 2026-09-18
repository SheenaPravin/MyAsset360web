"""Helpers that default family/member scope to the current user's family.

The web and mobile clients don't send family_id on creates, so the API
resolves it server-side: explicit value wins, otherwise the user's first
owned family, otherwise the first family they are a member of.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Family, FamilyMember, User


def resolve_family_id(db: Session, user: User, explicit: int | None = None) -> int:
    if explicit is not None:
        return explicit
    family = (
        db.query(Family).filter(Family.owner_id == user.id).order_by(Family.id).first()
    )
    if family is None:
        membership = (
            db.query(FamilyMember)
            .filter(FamilyMember.email == user.email)
            .order_by(FamilyMember.id)
            .first()
        )
        if membership is not None:
            return membership.family_id
    if family is None:
        raise HTTPException(
            status_code=400,
            detail="No family found for this account. Create a family first.",
        )
    return family.id


def resolve_member_id(
    db: Session, user: User, family_id: int, explicit: int | None = None
) -> int:
    if explicit is not None:
        return explicit
    member = (
        db.query(FamilyMember)
        .filter(FamilyMember.family_id == family_id)
        .order_by(FamilyMember.id)
        .first()
    )
    if member is None:
        raise HTTPException(
            status_code=400,
            detail="No family members found. Add a family member first.",
        )
    return member.id
