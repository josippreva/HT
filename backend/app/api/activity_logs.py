from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import ActivityLog, User
from app.api.deps import get_current_user


router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def list_activity_logs(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: int | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = (
        db.query(ActivityLog, User)
        .outerjoin(User, ActivityLog.user_id == User.id)
    )

    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)

    if action:
        query = query.filter(ActivityLog.action == action)

    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)

    if entity_id:
        query = query.filter(ActivityLog.entity_id == entity_id)

    if date_from:
        query = query.filter(ActivityLog.created_at >= date_from)

    if date_to:
        query = query.filter(ActivityLog.created_at <= date_to)

    if search:
        value = f"%{search}%"
        query = query.filter(
            ActivityLog.description.ilike(value)
            | ActivityLog.action.ilike(value)
            | ActivityLog.entity_type.ilike(value)
        )

    total = query.count()

    rows = (
        query
        .order_by(ActivityLog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "data": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": user.full_name if user else None,
                "user_email": user.email if user else None,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "old_data": log.old_data,
                "new_data": log.new_data,
                "created_at": log.created_at,
            }
            for log, user in rows
        ],
    }


@router.get("/{activity_log_id}")
def get_activity_log(
    activity_log_id: int,
    db: Session = Depends(get_db),
):
    row = (
        db.query(ActivityLog, User)
        .outerjoin(User, ActivityLog.user_id == User.id)
        .filter(ActivityLog.id == activity_log_id)
        .first()
    )

    if not row:
        return None

    log, user = row

    return {
        "id": log.id,
        "user_id": log.user_id,
        "user_name": user.full_name if user else None,
        "user_email": user.email if user else None,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "description": log.description,
        "old_data": log.old_data,
        "new_data": log.new_data,
        "created_at": log.created_at,
    }