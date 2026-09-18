import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Document, User
from app.schemas import schemas

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=list[schemas.DocumentOut])
def list_documents(
    family_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Document)
    if family_id is not None:
        q = q.filter(Document.family_id == family_id)
    return q.order_by(Document.id.desc()).all()


@router.post("/", response_model=schemas.DocumentOut)
def create_document_metadata(
    payload: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = Document(**payload.model_dump(), uploaded_by=current_user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/upload", response_model=schemas.DocumentOut)
def upload_document(
    family_id: int = Form(...),
    title: str = Form(...),
    category: str = Form(default="general"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    contents = file.file.read()
    dest.write_bytes(contents)
    doc = Document(
        family_id=family_id,
        title=title,
        category=category,
        file_path=str(dest),
        file_type=file.content_type or "",
        size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(
    doc_id: int,
    payload: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(doc, k, v)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except OSError:
        pass
    db.delete(doc)
    db.commit()
    return {"ok": True}
