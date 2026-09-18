from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    families: Mapped[list["Family"]] = orm_relationship("Family", back_populates="owner")


class Family(Base, TimestampMixin):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = orm_relationship("User", back_populates="families")
    members: Mapped[list["FamilyMember"]] = orm_relationship(
        "FamilyMember", back_populates="family", cascade="all, delete-orphan"
    )


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(100), default="")
    dob: Mapped[Date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), default="")
    role: Mapped[str] = mapped_column(String(20), default="member")  # admin/member/viewer
    phone: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(255), default="")

    family: Mapped["Family"] = orm_relationship("Family", back_populates="members")


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    member_id: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id", ondelete="SET NULL"), nullable=True
    )
    asset_type: Mapped[str] = mapped_column(String(50), default="other")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_value: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="")


class Liability(Base, TimestampMixin):
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    loan_type: Mapped[str] = mapped_column(String(100), default="personal")
    lender: Mapped[str] = mapped_column(String(255), default="")
    principal: Mapped[float] = mapped_column(Float, default=0.0)
    outstanding: Mapped[float] = mapped_column(Float, default=0.0)
    emi: Mapped[float] = mapped_column(Float, default=0.0)
    interest_rate: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")


class InsurancePolicy(Base, TimestampMixin):
    __tablename__ = "insurance_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    member_id: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id", ondelete="SET NULL"), nullable=True
    )
    policy_type: Mapped[str] = mapped_column(String(50), default="health")
    provider: Mapped[str] = mapped_column(String(255), default="")
    policy_number: Mapped[str] = mapped_column(String(255), default="")
    sum_insured: Mapped[float] = mapped_column(Float, default=0.0)
    premium: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")


class HealthProfile(Base, TimestampMixin):
    __tablename__ = "health_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey("family_members.id", ondelete="CASCADE"), unique=True, index=True
    )
    blood_group: Mapped[str] = mapped_column(String(10), default="")
    allergies: Mapped[str] = mapped_column(Text, default="")
    conditions: Mapped[str] = mapped_column(Text, default="")
    height: Mapped[float] = mapped_column(Float, default=0.0)  # cm
    weight: Mapped[float] = mapped_column(Float, default=0.0)  # kg


class MedicalRecord(Base, TimestampMixin):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey("family_members.id", ondelete="CASCADE"), index=True
    )
    record_type: Mapped[str] = mapped_column(String(100), default="general")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    hospital: Mapped[str] = mapped_column(String(255), default="")
    doctor: Mapped[str] = mapped_column(String(255), default="")
    visit_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )


class HealthcareExpense(Base, TimestampMixin):
    __tablename__ = "healthcare_expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    member_id: Mapped[int | None] = mapped_column(
        ForeignKey("family_members.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(100), default="general")
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    expense_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    hospital: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general")
    file_path: Mapped[str] = mapped_column(String(1024), default="")
    file_type: Mapped[str] = mapped_column(String(100), default="")
    size: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
