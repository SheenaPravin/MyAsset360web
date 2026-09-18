from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    Asset,
    Document,
    FamilyMember,
    HealthcareExpense,
    InsurancePolicy,
    Liability,
    Notification,
    User,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _scope(query, model, family_id: int | None):
    if family_id is not None:
        return query.filter(model.family_id == family_id)
    return query


@router.get("/dashboard")
def dashboard(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_assets = float(
        _scope(db.query(func.coalesce(func.sum(Asset.current_value), 0.0)), Asset, family_id).scalar()
        or 0.0
    )
    total_liabilities = float(
        _scope(
            db.query(func.coalesce(func.sum(Liability.outstanding), 0.0)),
            Liability,
            family_id,
        ).scalar()
        or 0.0
    )
    net_worth = total_assets - total_liabilities

    healthcare_spend = float(
        _scope(
            db.query(func.coalesce(func.sum(HealthcareExpense.amount), 0.0)),
            HealthcareExpense,
            family_id,
        ).scalar()
        or 0.0
    )

    # Expense by category
    cat_q = db.query(HealthcareExpense.category, func.sum(HealthcareExpense.amount))
    if family_id is not None:
        cat_q = cat_q.filter(HealthcareExpense.family_id == family_id)
    cat_q = cat_q.group_by(HealthcareExpense.category)
    expense_by_category = {cat or "general": float(total or 0) for cat, total in cat_q.all()}

    # Coverage gaps: members without health / life policy
    member_q = db.query(FamilyMember)
    policy_q = db.query(InsurancePolicy)
    if family_id is not None:
        member_q = member_q.filter(FamilyMember.family_id == family_id)
        policy_q = policy_q.filter(InsurancePolicy.family_id == family_id)
    members = member_q.all()
    policies = policy_q.all()
    covered_health = {p.member_id for p in policies if p.policy_type == "health"}
    covered_life = {p.member_id for p in policies if p.policy_type == "life"}
    coverage_gaps = []
    for m in members:
        missing = []
        if m.id not in covered_health:
            missing.append("health")
        if m.id not in covered_life:
            missing.append("life")
        if missing:
            coverage_gaps.append({"member_id": m.id, "name": m.name, "missing": missing})
    total_sum_insured = float(sum(p.sum_insured or 0 for p in policies))

    # Readiness indicator 0-100 (rule based)
    score = 50
    if net_worth > 0:
        score += 15
    if net_worth > total_liabilities:
        score += 10
    if members and len(coverage_gaps) == 0:
        score += 15
    elif members:
        score -= 10 * len(coverage_gaps)
    doc_count = _scope(db.query(func.count(Document.id)), Document, family_id).scalar() or 0
    if doc_count >= 5:
        score += 10
    upcoming_count = (
        _scope(
            db.query(func.count(Notification.id)).filter(
                Notification.is_read.is_(False),
                (Notification.due_date.is_(None))
                | (Notification.due_date >= date.today()),
            ),
            Notification,
            family_id,
        ).scalar()
        or 0
    )
    score = max(0, min(100, score))

    return {
        "family_id": family_id,
        "net_worth": net_worth,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_sum_insured": total_sum_insured,
        "coverage_gaps": coverage_gaps,
        "healthcare_spend": healthcare_spend,
        "expense_by_category": expense_by_category,
        "readiness_score": score,
        "counts": {
            "members": len(members),
            "policies": len(policies),
            "documents": int(doc_count),
            "upcoming_notifications": int(upcoming_count),
        },
    }


@router.get("/ai-insights")
def ai_insights(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rule-based insights (placeholder for future ML/AI)."""
    dash = dashboard(family_id=family_id, db=db, current_user=current_user)
    insights: list[dict] = []

    if dash["net_worth"] < 0:
        insights.append(
            {
                "severity": "high",
                "category": "wealth",
                "title": "Negative net worth",
                "message": "Liabilities exceed assets. Prioritise high-interest loan repayment.",
            }
        )
    if dash["total_liabilities"] > dash["total_assets"] * 0.5 and dash["total_assets"] > 0:
        insights.append(
            {
                "severity": "medium",
                "category": "wealth",
                "title": "High leverage",
                "message": "Outstanding loans exceed 50% of assets. Avoid new debt.",
            }
        )
    if dash["coverage_gaps"]:
        insights.append(
            {
                "severity": "high",
                "category": "insurance",
                "title": f"{len(dash['coverage_gaps'])} member(s) lack coverage",
                "message": "Some family members are missing health or life insurance.",
            }
        )
    # Expiring policies in 30 days
    soon = date.today() + timedelta(days=30)
    pq = db.query(InsurancePolicy).filter(
        InsurancePolicy.expiry_date.isnot(None),
        InsurancePolicy.expiry_date <= soon,
        InsurancePolicy.status == "active",
    )
    if family_id is not None:
        pq = pq.filter(InsurancePolicy.family_id == family_id)
    expiring = pq.all()
    if expiring:
        insights.append(
            {
                "severity": "medium",
                "category": "insurance",
                "title": f"{len(expiring)} polic(ies) expiring soon",
                "message": "Renew policies expiring within 30 days to avoid coverage lapse.",
            }
        )
    if dash["healthcare_spend"] > 0:
        top_cat = max(
            dash["expense_by_category"], key=lambda k: dash["expense_by_category"][k]
        )
        insights.append(
            {
                "severity": "info",
                "category": "health",
                "title": f"Top health spend: {top_cat}",
                "message": f"Total healthcare spend is {dash['healthcare_spend']:.2f}. Review '{top_cat}' costs.",
            }
        )
    if dash["readiness_score"] < 60:
        insights.append(
            {
                "severity": "medium",
                "category": "readiness",
                "title": "Low family readiness score",
                "message": "Improve readiness by uploading documents, closing coverage gaps, and building assets.",
            }
        )
    if not insights:
        insights.append(
            {
                "severity": "info",
                "category": "general",
                "title": "All looks good",
                "message": "No major risks detected. Keep tracking assets and health regularly.",
            }
        )
    return {"family_id": family_id, "insights": insights}
