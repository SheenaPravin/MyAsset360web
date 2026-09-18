from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash

# Import models so metadata is populated
from app.models import models  # noqa: F401
from app.routers import (
    analytics,
    assets,
    auth,
    documents,
    families,
    health,
    insurance,
    liabilities,
    notifications,
)


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        from app.models.models import (
            Asset,
            Family,
            FamilyMember,
            InsurancePolicy,
            Liability,
            Notification,
            User,
        )

        user = db.query(User).filter(User.email == "demo@myasset360.com").first()
        if user:
            return
        user = User(
            email="demo@myasset360.com",
            hashed_password=get_password_hash("demo1234"),
            full_name="Demo User",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        family = Family(name="Demo Family", owner_id=user.id)
        db.add(family)
        db.commit()
        db.refresh(family)

        member = FamilyMember(
            family_id=family.id,
            name="Demo User",
            relationship="self",
            gender="other",
            role="admin",
            email=user.email,
        )
        db.add(member)
        db.commit()
        db.refresh(member)

        db.add_all(
            [
                Asset(
                    family_id=family.id,
                    member_id=member.id,
                    asset_type="bank",
                    title="Savings Account",
                    description="Demo savings",
                    current_value=250000.0,
                    purchase_value=250000.0,
                ),
                Asset(
                    family_id=family.id,
                    member_id=member.id,
                    asset_type="investment",
                    title="Mutual Funds",
                    description="Demo investments",
                    current_value=500000.0,
                    purchase_value=400000.0,
                ),
                Asset(
                    family_id=family.id,
                    member_id=member.id,
                    asset_type="gold",
                    title="Gold",
                    description="Demo gold holdings",
                    current_value=150000.0,
                    purchase_value=120000.0,
                ),
            ]
        )
        db.add(
            Liability(
                family_id=family.id,
                loan_type="home",
                lender="Demo Bank",
                principal=2000000.0,
                outstanding=1500000.0,
                emi=18000.0,
                interest_rate=8.5,
                status="active",
            )
        )
        db.add(
            InsurancePolicy(
                family_id=family.id,
                member_id=member.id,
                policy_type="health",
                provider="Demo Insurance",
                policy_number="HLTH-0001",
                sum_insured=500000.0,
                premium=12000.0,
                expiry_date=date(date.today().year + 1, 3, 31),
                status="active",
            )
        )
        db.add(
            Notification(
                family_id=family.id,
                title="Welcome to MyAsset360",
                message="Demo data seeded successfully.",
                type="info",
                is_read=False,
            )
        )
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield


app = FastAPI(title="MyAsset360 API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(families.router)
app.include_router(assets.router)
app.include_router(liabilities.router)
app.include_router(insurance.router)
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"message": "MyAsset360 API running", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
