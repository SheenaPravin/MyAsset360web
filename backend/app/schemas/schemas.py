from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr

model_config = ConfigDict(from_attributes=True)


# ---------- Token / Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str  # email (OAuth2 compatible)
    password: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = ""


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime | None = None


# ---------- Family ----------
class FamilyBase(BaseModel):
    name: str


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    name: str | None = None


class FamilyOut(FamilyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime | None = None


# ---------- FamilyMember ----------
class FamilyMemberBase(BaseModel):
    name: str
    relationship: str = ""
    dob: date | None = None
    gender: str = ""
    role: str = "member"
    phone: str = ""
    email: str = ""


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    name: str | None = None
    relationship: str | None = None
    dob: date | None = None
    gender: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None


class FamilyMemberOut(FamilyMemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    family_id: int


# ---------- Asset ----------
class AssetBase(BaseModel):
    family_id: int
    member_id: int | None = None
    asset_type: str = "other"
    title: str
    description: str = ""
    current_value: float = 0.0
    purchase_value: float = 0.0
    purchase_date: date | None = None
    metadata_json: str = ""


class AssetCreate(AssetBase):
    family_id: int | None = None


class AssetUpdate(BaseModel):
    member_id: int | None = None
    asset_type: str | None = None
    title: str | None = None
    description: str | None = None
    current_value: float | None = None
    purchase_value: float | None = None
    purchase_date: date | None = None
    metadata_json: str | None = None


class AssetOut(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None


# ---------- Liability ----------
class LiabilityBase(BaseModel):
    family_id: int
    loan_type: str = "personal"
    lender: str = ""
    principal: float = 0.0
    outstanding: float = 0.0
    emi: float = 0.0
    interest_rate: float = 0.0
    start_date: date | None = None
    end_date: date | None = None
    status: str = "active"


class LiabilityCreate(LiabilityBase):
    family_id: int | None = None


class LiabilityUpdate(BaseModel):
    loan_type: str | None = None
    lender: str | None = None
    principal: float | None = None
    outstanding: float | None = None
    emi: float | None = None
    interest_rate: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


class LiabilityOut(LiabilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------- Insurance ----------
class InsuranceBase(BaseModel):
    family_id: int
    member_id: int | None = None
    policy_type: str = "health"
    provider: str = ""
    policy_number: str = ""
    sum_insured: float = 0.0
    premium: float = 0.0
    start_date: date | None = None
    expiry_date: date | None = None
    status: str = "active"


class InsuranceCreate(InsuranceBase):
    family_id: int | None = None


class InsuranceUpdate(BaseModel):
    member_id: int | None = None
    policy_type: str | None = None
    provider: str | None = None
    policy_number: str | None = None
    sum_insured: float | None = None
    premium: float | None = None
    start_date: date | None = None
    expiry_date: date | None = None
    status: str | None = None


class InsuranceOut(InsuranceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------- Health ----------
class HealthProfileBase(BaseModel):
    member_id: int
    blood_group: str = ""
    allergies: str = ""
    conditions: str = ""
    height: float = 0.0
    weight: float = 0.0


class HealthProfileCreate(HealthProfileBase):
    member_id: int | None = None


class HealthProfileUpdate(BaseModel):
    blood_group: str | None = None
    allergies: str | None = None
    conditions: str | None = None
    height: float | None = None
    weight: float | None = None


class HealthProfileOut(HealthProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MedicalRecordBase(BaseModel):
    member_id: int
    record_type: str = "general"
    title: str
    hospital: str = ""
    doctor: str = ""
    visit_date: date | None = None
    notes: str = ""
    document_id: int | None = None


class MedicalRecordCreate(MedicalRecordBase):
    member_id: int | None = None


class MedicalRecordUpdate(BaseModel):
    record_type: str | None = None
    title: str | None = None
    hospital: str | None = None
    doctor: str | None = None
    visit_date: date | None = None
    notes: str | None = None
    document_id: int | None = None


class MedicalRecordOut(MedicalRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class HealthcareExpenseBase(BaseModel):
    family_id: int
    member_id: int | None = None
    category: str = "general"
    amount: float = 0.0
    expense_date: date | None = None
    hospital: str = ""
    notes: str = ""


class HealthcareExpenseCreate(HealthcareExpenseBase):
    family_id: int | None = None


class HealthcareExpenseUpdate(BaseModel):
    member_id: int | None = None
    category: str | None = None
    amount: float | None = None
    expense_date: date | None = None
    hospital: str | None = None
    notes: str | None = None


class HealthcareExpenseOut(HealthcareExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------- Document ----------
class DocumentBase(BaseModel):
    family_id: int
    title: str
    category: str = "general"


class DocumentCreate(DocumentBase):
    family_id: int | None = None
    file_path: str = ""
    file_type: str = ""
    size: int = 0


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    family_id: int
    title: str
    category: str
    file_path: str
    file_type: str
    size: int
    uploaded_by: int | None = None
    created_at: datetime | None = None


# ---------- Notification ----------
class NotificationBase(BaseModel):
    family_id: int
    title: str
    message: str = ""
    due_date: date | None = None
    type: str = "info"


class NotificationCreate(NotificationBase):
    family_id: int | None = None


class NotificationUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    due_date: date | None = None
    type: str | None = None
    is_read: bool | None = None


class NotificationOut(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_read: bool
