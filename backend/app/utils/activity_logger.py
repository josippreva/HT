from app.models import ActivityLog


def log_activity(
    db,
    user,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None,
    old_data: dict | None = None,
    new_data: dict | None = None,
):
    activity = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_data=old_data,
        new_data=new_data,
    )

    db.add(activity)