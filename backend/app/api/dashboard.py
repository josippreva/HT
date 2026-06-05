from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import (
    Location,
    Device,
    NumberRange,
    RakNumberBlock,
    Subscriber,
    PhoneNumber,
    AreaCode,
    City,
    Region,
    Entity,
    User,
    ActivityLog,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)


def pct(part: int | float, total: int | float, digits: int = 1) -> float:
    return round((part / total * 100), digits) if total else 0.0


def status_count_expr(status: str):
    return func.count(case((PhoneNumber.status == status, PhoneNumber.id), else_=None))


ACTION_META = {
    "create":     ("ti ti-plus",        "blue"),
    "update":     ("ti ti-edit",        "blue"),
    "delete":     ("ti ti-trash",       "red"),
    "assign":     ("ti ti-phone-check", "blue"),
    "release":    ("ti ti-phone-off",   "amber"),
    "quarantine": ("ti ti-clock",       "amber"),
    "login":      ("ti ti-login",       "gray"),
    "logout":     ("ti ti-logout",      "gray"),
    "generate":   ("ti ti-cpu",         "blue"),
}


# ── /dashboard/stats ────────────────────────────────────────────────────────

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total      = db.query(func.count(PhoneNumber.id)).scalar() or 0
    free       = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "slobodan").scalar() or 0
    busy       = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "zauzet").scalar() or 0
    quarantine = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "karantena").scalar() or 0

    ranges_total     = db.query(func.count(NumberRange.id)).scalar() or 0
    ranges_generated = db.query(func.count(NumberRange.id)).filter(NumberRange.generated == True).scalar() or 0

    return {
        "locations":           db.query(func.count(Location.id)).scalar() or 0,
        "devices":             db.query(func.count(Device.id)).scalar() or 0,
        "ranges":              ranges_total,
        "ranges_generated":    ranges_generated,
        "ranges_not_generated": ranges_total - ranges_generated,
        "rak_blocks":          db.query(func.count(RakNumberBlock.id)).scalar() or 0,
        "subscribers":         db.query(func.count(Subscriber.id)).scalar() or 0,
        "phone_numbers_total": total,
        "free":                free,
        "busy":                busy,
        "quarantine":          quarantine,
    }


# ── /dashboard/analytics ────────────────────────────────────────────────────

@router.get("/analytics")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # ── Brojevi po statusu ───────────────────────────────────────────────────
    total      = db.query(func.count(PhoneNumber.id)).scalar() or 0
    free       = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "slobodan").scalar() or 0
    busy       = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "zauzet").scalar() or 0
    quarantine = db.query(func.count(PhoneNumber.id)).filter(PhoneNumber.status == "karantena").scalar() or 0
    other      = max(total - free - busy - quarantine, 0)

    rak_total_capacity = db.query(func.sum(RakNumberBlock.block_size)).scalar() or 0

    # ── Rasponi ──────────────────────────────────────────────────────────────
    ranges_total         = db.query(func.count(NumberRange.id)).scalar() or 0
    ranges_generated     = db.query(func.count(NumberRange.id)).filter(NumberRange.generated == True).scalar() or 0
    ranges_not_generated = ranges_total - ranges_generated

    # ── Lokacije i uređaji ───────────────────────────────────────────────────
    locations_total  = db.query(func.count(Location.id)).scalar() or 0
    devices_total    = db.query(func.count(Device.id)).scalar() or 0
    devices_active   = db.query(func.count(Device.id)).filter(Device.active == True).scalar() or 0
    devices_inactive = devices_total - devices_active

    # ── Gradovi i poštanski brojevi ──────────────────────────────────────────
    cities_count = db.query(func.count(City.id)).scalar() or 0

    from app.models import PostalCode
    postal_codes_count = db.query(func.count(PostalCode.id)).scalar() or 0

    # ── Pretplatnici ─────────────────────────────────────────────────────────
    sub_total    = db.query(func.count(Subscriber.id)).scalar() or 0
    sub_physical = (
        db.query(func.count(Subscriber.id))
        .filter(Subscriber.subscriber_type == "physical_person")
        .scalar() or 0
    )
    sub_legal = (
        db.query(func.count(Subscriber.id))
        .filter(Subscriber.subscriber_type == "legal_entity")
        .scalar() or 0
    )
    multi_number_subs = (
        db.query(func.count())
        .select_from(
            db.query(PhoneNumber.subscriber_id)
            .filter(PhoneNumber.subscriber_id.isnot(None))
            .group_by(PhoneNumber.subscriber_id)
            .having(func.count(PhoneNumber.id) > 1)
            .subquery()
        )
        .scalar() or 0
    )

    # ── RAK blokovi ──────────────────────────────────────────────────────────
    rak_blocks_raw = (
        db.query(
            RakNumberBlock.id,
            RakNumberBlock.block_start,
            RakNumberBlock.block_end,
            RakNumberBlock.operator_name,
            RakNumberBlock.block_size,
            AreaCode.code.label("area_code"),
            AreaCode.name.label("area_code_name"),
            Region.name.label("region_name"),
        )
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .join(Region, AreaCode.region_id == Region.id)
        .order_by(AreaCode.code, RakNumberBlock.block_start)
        .all()
    )

    rak_blocks = []
    for rb in rak_blocks_raw:
        base             = db.query(PhoneNumber.id).join(NumberRange, PhoneNumber.number_range_id == NumberRange.id).filter(NumberRange.rak_block_id == rb.id)
        generated_numbers = base.count() or 0
        free_in_block    = base.filter(PhoneNumber.status == "slobodan").count() or 0
        busy_in_block    = base.filter(PhoneNumber.status == "zauzet").count() or 0
        quarantine_in_block = base.filter(PhoneNumber.status == "karantena").count() or 0

        ranges_total_count = db.query(func.count(NumberRange.id)).filter(NumberRange.rak_block_id == rb.id).scalar() or 0
        ranges_generated_count = (
            db.query(func.count(NumberRange.id))
            .filter(NumberRange.rak_block_id == rb.id, NumberRange.generated == True)
            .scalar() or 0
        )

        rak_blocks.append({
            "id":                   rb.id,
            "operator_name":        rb.operator_name,
            "area_code":            rb.area_code,
            "area_code_name":       rb.area_code_name,
            "region_name":          rb.region_name,
            "block_start":          rb.block_start,
            "block_end":            rb.block_end,
            "block_size":           rb.block_size,
            "generated_numbers":    generated_numbers,
            "not_generated_numbers": max(rb.block_size - generated_numbers, 0),
            "free":                 free_in_block,
            "busy":                 busy_in_block,
            "quarantine":           quarantine_in_block,
            "gen_pct":              pct(generated_numbers, rb.block_size),
            "usage_pct":            pct(busy_in_block, generated_numbers),
            "free_pct":             pct(free_in_block, generated_numbers),
            "ranges_total":         ranges_total_count,
            "ranges_generated":     ranges_generated_count,
            "ranges_not_generated": ranges_total_count - ranges_generated_count,
        })

    # ── Kritični rasponi ─────────────────────────────────────────────────────
    critical_ranges_raw = (
        db.query(
            NumberRange.id,
            NumberRange.name,
            NumberRange.range_start,
            NumberRange.range_end,
            NumberRange.range_size,
            Location.name.label("location_name"),
            City.name.label("city_name"),
            RakNumberBlock.id.label("rak_block_id"),
            RakNumberBlock.block_start.label("rak_block_start"),
            RakNumberBlock.block_end.label("rak_block_end"),
            RakNumberBlock.operator_name,
            AreaCode.code.label("area_code"),
            status_count_expr("slobodan").label("free"),
            status_count_expr("zauzet").label("busy"),
            status_count_expr("karantena").label("quarantine"),
            func.count(PhoneNumber.id).label("generated_numbers"),
        )
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Region, City.region_id == Region.id)
        .join(Entity, Region.entity_id == Entity.id)
        .outerjoin(Device, NumberRange.device_id == Device.id)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .outerjoin(PhoneNumber, PhoneNumber.number_range_id == NumberRange.id)
        .filter(NumberRange.generated == True)
        .group_by(
            NumberRange.id,
            NumberRange.name,
            NumberRange.range_start,
            NumberRange.range_end,
            NumberRange.range_size,
            Location.name,
            City.name,
            RakNumberBlock.id,
            RakNumberBlock.block_start,
            RakNumberBlock.block_end,
            RakNumberBlock.operator_name,
            AreaCode.code,
        )
        .all()
    )

    critical_ranges = sorted(
        [
            {
                "id":               r.id,
                "name":             r.name or f"{r.range_start}–{r.range_end}",
                "range_start":      r.range_start,
                "range_end":        r.range_end,
                "range_size":       r.range_size,
                "location_name":    r.location_name,
                "city_name":        r.city_name,
                "rak_block_id":     r.rak_block_id,
                "rak_block_start":  r.rak_block_start,
                "rak_block_end":    r.rak_block_end,
                "operator_name":    r.operator_name,
                "area_code":        r.area_code,
                "free":             r.free or 0,
                "busy":             r.busy or 0,
                "quarantine":       r.quarantine or 0,
                "generated_numbers": r.generated_numbers or 0,
                "usage_pct":        pct(r.busy or 0, r.generated_numbers or 0),
                "free_pct":         pct(r.free or 0, r.generated_numbers or 0),
            }
            for r in critical_ranges_raw
            if (r.generated_numbers or 0) > 0
        ],
        key=lambda x: (x["usage_pct"], -x["free"]),
        reverse=True,
    )[:8]

    # ── Kategorije brojeva ───────────────────────────────────────────────────
    categories_raw = (
        db.query(
            PhoneNumber.number_category,
            func.count(PhoneNumber.id).label("total"),
            status_count_expr("slobodan").label("free"),
            status_count_expr("zauzet").label("busy"),
            status_count_expr("karantena").label("quarantine"),
        )
        .group_by(PhoneNumber.number_category)
        .order_by(func.count(PhoneNumber.id).desc())
        .all()
    )
    categories = [
        {
            "category":   r.number_category or "standard",
            "total":      r.total,
            "free":       r.free,
            "busy":       r.busy,
            "quarantine": r.quarantine,
            "usage_pct":  pct(r.busy, r.total),
        }
        for r in categories_raw
    ]

    # ── Mjesečni trend ───────────────────────────────────────────────────────
    monthly_trend = []
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for i in range(5, -1, -1):
        rough       = first_of_this_month - timedelta(days=31 * i)
        month_start = rough.replace(day=1)
        next_month  = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end   = min(next_month, now)

        assigned_count = (
            db.query(func.count(PhoneNumber.id))
            .filter(PhoneNumber.assigned_at >= month_start, PhoneNumber.assigned_at < month_end)
            .scalar() or 0
        )
        quarantine_count = (
            db.query(func.count(PhoneNumber.id))
            .filter(PhoneNumber.quarantine_at >= month_start, PhoneNumber.quarantine_at < month_end)
            .scalar() or 0
        )

        monthly_trend.append({
            "month":     month_start.strftime("%b %Y"),
            "month_iso": month_start.strftime("%Y-%m"),
            "assigned":  assigned_count,
            "released":  quarantine_count,
            "net":       assigned_count - quarantine_count,
        })

    # ── Prvi slobodni broj ───────────────────────────────────────────────────
    first_free_row = (
        db.query(
            PhoneNumber.id,
            PhoneNumber.number_value,
            PhoneNumber.number_category,
            NumberRange.id.label("range_id"),
            NumberRange.name.label("range_name"),
            Location.id.label("location_id"),
            Location.name.label("location_name"),
            City.id.label("city_id"),
            City.name.label("city_name"),
            AreaCode.code.label("area_code"),
        )
        .join(NumberRange, PhoneNumber.number_range_id == NumberRange.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .filter(PhoneNumber.status == "slobodan")
        .order_by(PhoneNumber.number_value)
        .first()
    )
    first_free = None
    if first_free_row:
        first_free = {
            "id":              first_free_row.id,
            "number_value":    first_free_row.number_value,
            "number_category": first_free_row.number_category,
            "range_id":        first_free_row.range_id,
            "range_name":      first_free_row.range_name,
            "location_id":     first_free_row.location_id,
            "location_name":   first_free_row.location_name,
            "city_id":         first_free_row.city_id,
            "city_name":       first_free_row.city_name,
            "area_code":       first_free_row.area_code,
        }

    # ── Nedavne aktivnosti (iz ActivityLog) ──────────────────────────────────
    recent_rows = (
        db.query(ActivityLog, User)
        .outerjoin(User, ActivityLog.user_id == User.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )

    recent_activities = []
    for log, user in recent_rows:
        icon, tone = ACTION_META.get(log.action, ("ti ti-activity", "gray"))

        if user:
            user_label = user.full_name or user.email or f"Korisnik #{log.user_id}"
        elif log.user_id:
            user_label = f"Korisnik #{log.user_id}"
        else:
            user_label = None

        recent_activities.append({
            "title":       log.description or f"{log.action} — {log.entity_type}",
            "subtitle":    user_label or "Sustav",
            "action":      log.action,
            "entity_type": log.entity_type,
            "entity_id":   log.entity_id,
            "icon":        icon,
            "tone":        tone,
            "time":        log.created_at.isoformat() if log.created_at else None,
            "user_id":     log.user_id,
            "user_name":   user_label,
        })

    # ── Upozorenja ───────────────────────────────────────────────────────────
    assigned_without_subscriber = (
        db.query(func.count(PhoneNumber.id))
        .filter(PhoneNumber.status == "zauzet", PhoneNumber.subscriber_id.is_(None))
        .scalar() or 0
    )
    exhausted_ranges = (
        db.query(func.count(NumberRange.id))
        .filter(NumberRange.generated == True)
        .filter(
            ~NumberRange.id.in_(
                db.query(PhoneNumber.number_range_id)
                .filter(PhoneNumber.status == "slobodan")
                .distinct()
            )
        )
        .scalar() or 0
    )
    generated_empty_ranges = (
        db.query(func.count(NumberRange.id))
        .filter(NumberRange.generated == True)
        .filter(
            ~NumberRange.id.in_(
                db.query(PhoneNumber.number_range_id).distinct()
            )
        )
        .scalar() or 0
    )
    old_quarantine = (
        db.query(func.count(PhoneNumber.id))
        .filter(PhoneNumber.status == "karantena", PhoneNumber.quarantine_at < now - timedelta(days=90))
        .scalar() or 0
    )

    warnings = []
    for r in [x for x in critical_ranges if x["usage_pct"] >= 85][:4]:
        warnings.append({
            "type":     "high_usage_range",
            "severity": "danger" if r["usage_pct"] >= 95 else "warning",
            "message":  f"Raspon {r['range_start']}–{r['range_end']} je na {r['usage_pct']}% iskorištenosti ({r['free']} slobodno)",
        })
    if exhausted_ranges:
        warnings.append({"type": "exhausted_ranges",      "severity": "warning", "message": f"{exhausted_ranges} generiranih raspona nema slobodnih brojeva"})
    if old_quarantine:
        warnings.append({"type": "old_quarantine",        "severity": "info",    "message": f"{old_quarantine} brojeva je u karanteni dulje od 90 dana"})
    if assigned_without_subscriber:
        warnings.append({"type": "data_quality",          "severity": "danger",  "message": f"{assigned_without_subscriber} zauzetih brojeva nema vezanog pretplatnika"})
    if generated_empty_ranges:
        warnings.append({"type": "generated_empty_ranges","severity": "warning", "message": f"{generated_empty_ranges} generiranih raspona nema generirane brojeve"})

    # ── Response ─────────────────────────────────────────────────────────────
    return {
        "generated_at": now.isoformat(),
        "summary": {
            "rak_total_capacity":      rak_total_capacity,
            "generated_total":         total,
            "gen_pct":                 pct(total, rak_total_capacity),
            "free":                    free,
            "free_pct":                pct(free, total),
            "busy":                    busy,
            "busy_pct":                pct(busy, total),
            "quarantine":              quarantine,
            "quarantine_pct":          pct(quarantine, total),
            "other":                   other,
            "locations":               locations_total,
            "devices":                 devices_total,
            "devices_active":          devices_active,
            "devices_inactive":        devices_inactive,
            "rak_blocks_count":        db.query(func.count(RakNumberBlock.id)).scalar() or 0,
            "ranges_total":            ranges_total,
            "ranges_generated":        ranges_generated,
            "ranges_not_generated":    ranges_not_generated,
            "subscribers_total":       sub_total,
            "subscribers_physical":    sub_physical,
            "subscribers_legal":       sub_legal,
            "subscribers_multi_number": multi_number_subs,
            "cities_count":            cities_count,
            "postal_codes_count":      postal_codes_count,
        },
        "rak_blocks":        rak_blocks,
        "critical_ranges":   critical_ranges,
        "categories":        categories,
        "monthly_trend":     monthly_trend,
        "first_free":        first_free,
        "recent_activities": recent_activities,
        "warnings":          warnings,
    }


# ── /dashboard/first-free ────────────────────────────────────────────────────

@router.get("/first-free")
def get_first_free_number(
    db: Session = Depends(get_db),
    entity_id:       Optional[int] = Query(None),
    region_id:       Optional[int] = Query(None),
    city_id:         Optional[int] = Query(None),
    location_id:     Optional[int] = Query(None),
    device_id:       Optional[int] = Query(None),
    area_code:       Optional[str] = Query(None),
    number_category: Optional[str] = Query(None),
    rak_block_id:    Optional[int] = Query(None),
    number_range_id: Optional[int] = Query(None),
):
    query = (
        db.query(
            PhoneNumber.id,
            PhoneNumber.number_value,
            PhoneNumber.number_category,
            NumberRange.id.label("range_id"),
            NumberRange.name.label("range_name"),
            Location.id.label("location_id"),
            Location.name.label("location_name"),
            City.id.label("city_id"),
            City.name.label("city_name"),
            Region.id.label("region_id"),
            Region.name.label("region_name"),
            Entity.id.label("entity_id"),
            Entity.name.label("entity_name"),
            Device.id.label("device_id"),
            Device.name.label("device_name"),
            RakNumberBlock.id.label("rak_block_id"),
            RakNumberBlock.block_start.label("rak_block_start"),
            RakNumberBlock.block_end.label("rak_block_end"),
            AreaCode.code.label("area_code"),
        )
        .join(NumberRange, PhoneNumber.number_range_id == NumberRange.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Region, City.region_id == Region.id)
        .join(Entity, Region.entity_id == Entity.id)
        .outerjoin(Device, NumberRange.device_id == Device.id)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .filter(PhoneNumber.status == "slobodan")
    )

    if entity_id:       query = query.filter(Entity.id == entity_id)
    if region_id:       query = query.filter(Region.id == region_id)
    if city_id:         query = query.filter(City.id == city_id)
    if location_id:     query = query.filter(Location.id == location_id)
    if device_id:       query = query.filter(NumberRange.device_id == device_id)
    if area_code:       query = query.filter(AreaCode.code == area_code)
    if number_category: query = query.filter(PhoneNumber.number_category == number_category)
    if rak_block_id:    query = query.filter(RakNumberBlock.id == rak_block_id)
    if number_range_id: query = query.filter(NumberRange.id == number_range_id)

    row = query.order_by(PhoneNumber.number_value).first()

    if not row:
        return {"found": False, "number": None}

    return {
        "found": True,
        "number": {
            "id":              row.id,
            "number_value":    row.number_value,
            "number_category": row.number_category,
            "range_id":        row.range_id,
            "range_name":      row.range_name,
            "location_id":     row.location_id,
            "location_name":   row.location_name,
            "city_id":         row.city_id,
            "city_name":       row.city_name,
            "region_id":       row.region_id,
            "region_name":     row.region_name,
            "entity_id":       row.entity_id,
            "entity_name":     row.entity_name,
            "device_id":       row.device_id,
            "device_name":     row.device_name,
            "rak_block_id":    row.rak_block_id,
            "rak_block_start": row.rak_block_start,
            "rak_block_end":   row.rak_block_end,
            "area_code":       row.area_code,
        },
    }


# ── /dashboard/ranges ────────────────────────────────────────────────────────

@router.get("/ranges")
def get_dashboard_ranges(
    db: Session = Depends(get_db),
    search:       Optional[str]  = Query(None),
    city_id:      Optional[int]  = Query(None),
    rak_block_id: Optional[int]  = Query(None),
    generated:    Optional[bool] = Query(None),
    sort_critical: Optional[bool] = Query(None),
    page:         int = Query(1, ge=1),
    page_size:    int = Query(15, ge=5, le=100),
):
    query = (
        db.query(
            NumberRange.id,
            NumberRange.name,
            NumberRange.range_start,
            NumberRange.range_end,
            NumberRange.range_size,
            NumberRange.generated,
            Location.name.label("location_name"),
            City.id.label("city_id"),
            City.name.label("city_name"),
            RakNumberBlock.id.label("rak_block_id"),
            RakNumberBlock.block_start.label("rak_block_start"),
            RakNumberBlock.block_end.label("rak_block_end"),
            RakNumberBlock.operator_name,
            AreaCode.code.label("area_code"),
            status_count_expr("slobodan").label("free_count"),
            status_count_expr("zauzet").label("busy_count"),
            status_count_expr("karantena").label("quar_count"),
            func.count(PhoneNumber.id).label("total_numbers"),
        )
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .outerjoin(PhoneNumber, PhoneNumber.number_range_id == NumberRange.id)
        .group_by(
            NumberRange.id,
            Location.name,
            City.id,
            City.name,
            RakNumberBlock.id,
            RakNumberBlock.block_start,
            RakNumberBlock.block_end,
            RakNumberBlock.operator_name,
            AreaCode.code,
        )
    )

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                NumberRange.name.ilike(like),
                NumberRange.range_start.ilike(like),
                NumberRange.range_end.ilike(like),
            )
        )
    if city_id:           query = query.filter(City.id == city_id)
    if rak_block_id:      query = query.filter(RakNumberBlock.id == rak_block_id)
    if generated is not None: query = query.filter(NumberRange.generated == generated)

    total_count = query.count()

    if sort_critical:
        subq = query.subquery()
        from sqlalchemy import desc
        busy_col   = subq.c.busy_count
        total_col  = subq.c.total_numbers
        usage_expr = case((total_col > 0, busy_col * 100.0 / total_col), else_=0)
        ranges_raw = (
            db.query(subq)
            .filter(subq.c.generated == True)
            .order_by(desc(usage_expr), subq.c.free_count)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
    else:
        ranges_raw = (
            query.order_by(NumberRange.range_start)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    ranges_list = []
    for r in ranges_raw:
        total_numbers = r.total_numbers if r.generated else 0
        ranges_list.append({
            "id":            r.id,
            "name":          r.name or f"{r.range_start}–{r.range_end}",
            "range_start":   r.range_start,
            "range_end":     r.range_end,
            "range_size":    r.range_size,
            "generated":     r.generated,
            "location_name": r.location_name,
            "city_id":       r.city_id,
            "city_name":     r.city_name,
            "rak_block_id":  r.rak_block_id,
            "rak_block_start": r.rak_block_start,
            "rak_block_end":   r.rak_block_end,
            "operator_name": r.operator_name,
            "area_code":     r.area_code,
            "free":          r.free_count if r.generated else None,
            "busy":          r.busy_count if r.generated else None,
            "quarantine":    r.quar_count if r.generated else None,
            "total_numbers": total_numbers,
            "usage_pct":     pct(r.busy_count, total_numbers) if r.generated else 0,
        })

    cities_raw = (
        db.query(City.id, City.name)
        .join(Location, Location.city_id == City.id)
        .join(NumberRange, NumberRange.location_id == Location.id)
        .distinct()
        .order_by(City.name)
        .all()
    )
    cities = [{"id": c.id, "name": c.name} for c in cities_raw]

    rak_filter_raw = (
        db.query(
            RakNumberBlock.id,
            RakNumberBlock.operator_name,
            AreaCode.code,
            RakNumberBlock.block_start,
            RakNumberBlock.block_end,
        )
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .order_by(AreaCode.code, RakNumberBlock.block_start)
        .all()
    )
    rak_blocks_filter = [
        {
            "id":    r.id,
            "label": f"{r.code} | {r.block_start}–{r.block_end} | {r.operator_name}",
        }
        for r in rak_filter_raw
    ]

    pages = (total_count + page_size - 1) // page_size if total_count else 1

    return {
        "ranges":            ranges_list,
        "total":             total_count,
        "page":              page,
        "page_size":         page_size,
        "pages":             pages,
        "filter_cities":     cities,
        "filter_rak_blocks": rak_blocks_filter,
    }