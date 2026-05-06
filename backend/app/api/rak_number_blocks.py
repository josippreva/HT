from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import RakNumberBlock, AreaCode, Region
from app.schemas.rak_number_block import RakNumberBlockCreate
from app.api.deps import get_current_user
router = APIRouter(prefix="/rak-number-blocks", tags=["RAK Number Blocks"],dependencies=[Depends(get_current_user)])


def calculate_block_size(block_start: str, block_end: str) -> int:
    return int(block_end) - int(block_start) + 1


def validate_block_range(block_start: str, block_end: str) -> None:
    if int(block_start) >= int(block_end):
        raise HTTPException(
            status_code=400,
            detail="Početak bloka mora biti manji od kraja bloka",
        )


def check_overlap(
    db: Session,
    block_start: str,
    block_end: str,
    exclude_id: int | None = None,
) -> None:
    query = db.query(RakNumberBlock).filter(
        RakNumberBlock.block_start <= block_end,
        RakNumberBlock.block_end >= block_start,
    )

    if exclude_id:
        query = query.filter(RakNumberBlock.id != exclude_id)

    existing = query.first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Blok se preklapa s postojećim blokom {existing.block_start} - {existing.block_end}",
        )


@router.get("")
def list_rak_number_blocks(
    area_code_id: int | None = Query(default=None),
    operator_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(RakNumberBlock, AreaCode, Region)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .join(Region, AreaCode.region_id == Region.id)
    )

    if area_code_id:
        query = query.filter(RakNumberBlock.area_code_id == area_code_id)

    if operator_name:
        query = query.filter(RakNumberBlock.operator_name.ilike(f"%{operator_name}%"))

    rows = query.order_by(AreaCode.code, RakNumberBlock.block_start).all()

    return [
        {
            "id": block.id,
            "area_code_id": block.area_code_id,
            "operator_name": block.operator_name,
            "block_start": block.block_start,
            "block_end": block.block_end,
            "block_size": block.block_size,
            "source_file": block.source_file,
            "area_code": area_code.code,
            "area_name": area_code.name,
            "region_name": region.name,
        }
        for block, area_code, region in rows
    ]


@router.get("/{block_id}")
def get_rak_number_block(block_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(RakNumberBlock, AreaCode, Region)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .join(Region, AreaCode.region_id == Region.id)
        .filter(RakNumberBlock.id == block_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="RAK blok nije pronađen")

    block, area_code, region = row

    return {
        "id": block.id,
        "area_code_id": block.area_code_id,
        "operator_name": block.operator_name,
        "block_start": block.block_start,
        "block_end": block.block_end,
        "block_size": block.block_size,
        "source_file": block.source_file,
        "area_code": area_code.code,
        "area_name": area_code.name,
        "region_name": region.name,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_rak_number_block(
    data: RakNumberBlockCreate,
    db: Session = Depends(get_db),
):
    area_code = db.query(AreaCode).filter(AreaCode.id == data.area_code_id).first()

    if not area_code:
        raise HTTPException(status_code=404, detail="Pozivni broj nije pronađen")

    validate_block_range(data.block_start, data.block_end)
    check_overlap(db, data.block_start, data.block_end)

    block = RakNumberBlock(
        area_code_id=data.area_code_id,
        operator_name=data.operator_name,
        block_start=data.block_start,
        block_end=data.block_end,
        block_size=calculate_block_size(data.block_start, data.block_end),
        source_file=data.source_file,
    )

    db.add(block)
    db.commit()
    db.refresh(block)

    return block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rak_number_block(block_id: int, db: Session = Depends(get_db)):
    block = db.query(RakNumberBlock).filter(RakNumberBlock.id == block_id).first()

    if not block:
        raise HTTPException(status_code=404, detail="RAK blok nije pronađen")

    db.delete(block)
    db.commit()

    return None