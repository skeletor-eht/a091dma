"""
History and Templates router
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import User, RewriteVersion, Template, TimeEntry
from ..schemas import (
    RewriteVersionOut,
    TemplateCreate,
    TemplateUpdate,
    TemplateOut,
)
from ..deps import get_current_user, check_client_access

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== VERSION HISTORY ==========


@router.get("/versions/{time_entry_id}", response_model=List[RewriteVersionOut])
def get_time_entry_versions(
    time_entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions for a specific time entry"""
    # First check if time entry exists
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    # Check if user has access to this client
    if not check_client_access(current_user, time_entry.client_id, db):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this time entry"
        )

    # Get all versions
    versions = db.query(RewriteVersion).filter(
        RewriteVersion.time_entry_id == time_entry_id
    ).order_by(
        RewriteVersion.version_number.desc()
    ).all()

    return versions


@router.post("/versions/{time_entry_id}/restore/{version_id}")
def restore_version(
    time_entry_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restore a previous version as the current version"""
    # Check access
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    if not check_client_access(current_user, time_entry.client_id, db):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this time entry"
        )

    # Get the version to restore
    version = db.query(RewriteVersion).filter(
        RewriteVersion.id == version_id,
        RewriteVersion.time_entry_id == time_entry_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Get the highest version number
    max_version = db.query(RewriteVersion).filter(
        RewriteVersion.time_entry_id == time_entry_id
    ).count()

    # Create a new version based on the old one
    new_version = RewriteVersion(
        id=str(uuid.uuid4()),
        time_entry_id=time_entry_id,
        version_number=max_version + 1,
        standard=version.standard,
        client_compliant=version.client_compliant,
        audit_safe=version.audit_safe,
        notes=f"Restored from version {version.version_number}",
        created_by=current_user.username,
        is_current=True,
    )
    db.add(new_version)

    # Mark all other versions as not current
    db.query(RewriteVersion).filter(
        RewriteVersion.time_entry_id == time_entry_id
    ).update({"is_current": False})

    new_version.is_current = True

    db.commit()
    db.refresh(new_version)

    return {
        "status": "success",
        "message": f"Restored version {version.version_number} as version {new_version.version_number}",
        "new_version": RewriteVersionOut.model_validate(new_version)
    }


# ========== TEMPLATES ==========


@router.post("/templates", response_model=TemplateOut)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new template"""
    # If client_id specified, verify access
    if template.client_id:
        if not check_client_access(current_user, template.client_id, db):
            raise HTTPException(
                status_code=403,
                detail=f"You do not have permission to access client {template.client_id}"
            )

    new_template = Template(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        client_id=template.client_id,
        name=template.name,
        template_type=template.template_type,
        original_text=template.original_text,
        rewrite_text=template.rewrite_text,
        category=template.category,
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.get("/templates", response_model=List[TemplateOut])
def list_templates(
    client_id: Optional[str] = None,
    template_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all templates for current user"""
    query = db.query(Template).filter(Template.user_id == current_user.id)

    if client_id:
        query = query.filter(Template.client_id == client_id)

    if template_type:
        query = query.filter(Template.template_type == template_type)

    if category:
        query = query.filter(Template.category == category)

    templates = query.order_by(Template.updated_at.desc()).all()

    return templates


@router.get("/templates/{template_id}", response_model=TemplateOut)
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.put("/templates/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: str,
    update: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields if provided
    if update.name is not None:
        template.name = update.name
    if update.rewrite_text is not None:
        template.rewrite_text = update.rewrite_text
    if update.category is not None:
        template.category = update.category

    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return template


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()

    return {"status": "success", "message": "Template deleted"}


@router.post("/templates/{template_id}/use")
def use_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Increment usage count for a template"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.usage_count += 1
    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return template
