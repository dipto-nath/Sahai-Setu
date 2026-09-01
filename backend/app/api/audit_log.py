"""
Audit Log API Routes for SIH26093
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.users import User
from app.models.audit_log import AuditLog
from app.database import get_db
from app.api.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/audit-log", tags=["Audit Log"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_audit_log(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    case_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_admin)
):
    """Get audit log entries (admin only)."""
    db = next(get_db())
    try:
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if case_id:
            query = query.filter(AuditLog.case_id == case_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "case_id": log.case_id,
                "metadata": log.metadata,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            for log in logs
        ]
    finally:
        db.close()
