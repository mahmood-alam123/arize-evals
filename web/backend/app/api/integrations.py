"""API routes for webhook integrations (Slack, Teams)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db, IntegrationConfig
from ..schemas import (
    IntegrationConfigCreate,
    IntegrationConfigUpdate,
    IntegrationConfigResponse,
)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("", response_model=List[IntegrationConfigResponse])
def list_integrations(db: Session = Depends(get_db)):
    """List all webhook integrations."""
    integrations = db.query(IntegrationConfig).order_by(IntegrationConfig.created_at.desc()).all()
    return [IntegrationConfigResponse.model_validate(i) for i in integrations]


@router.get("/{integration_id}", response_model=IntegrationConfigResponse)
def get_integration(integration_id: int, db: Session = Depends(get_db)):
    """Get a specific webhook integration."""
    integration = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_id
    ).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return IntegrationConfigResponse.model_validate(integration)


@router.post("", response_model=IntegrationConfigResponse, status_code=201)
def create_integration(
    config: IntegrationConfigCreate,
    db: Session = Depends(get_db),
):
    """Create a new webhook integration."""
    integration = IntegrationConfig(
        integration_type=config.integration_type,
        webhook_url=config.webhook_url,
        is_active=config.is_active,
        notify_on_pass=config.notify_on_pass,
        notify_on_fail=config.notify_on_fail,
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return IntegrationConfigResponse.model_validate(integration)


@router.put("/{integration_id}", response_model=IntegrationConfigResponse)
def update_integration(
    integration_id: int,
    config: IntegrationConfigUpdate,
    db: Session = Depends(get_db),
):
    """Update a webhook integration."""
    integration = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_id
    ).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if config.webhook_url is not None:
        integration.webhook_url = config.webhook_url
    if config.is_active is not None:
        integration.is_active = config.is_active
    if config.notify_on_pass is not None:
        integration.notify_on_pass = config.notify_on_pass
    if config.notify_on_fail is not None:
        integration.notify_on_fail = config.notify_on_fail

    db.commit()
    db.refresh(integration)
    return IntegrationConfigResponse.model_validate(integration)


@router.delete("/{integration_id}", status_code=204)
def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    """Delete a webhook integration."""
    integration = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_id
    ).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    db.delete(integration)
    db.commit()
