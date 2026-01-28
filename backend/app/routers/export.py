from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.db import crud
from app.services.calendar_export import create_ics_calendar, create_json_export, create_csv_export

router = APIRouter()


@router.get("/ics")
async def export_ics(
    syllabus_id: Optional[int] = Query(None, description="Filter by syllabus"),
    db: AsyncSession = Depends(get_db)
):
    """Export assignments as ICS calendar file."""
    assignments = await crud.get_all_assignments(db, syllabus_id)

    calendar_name = "Syllabus Assignments"
    if syllabus_id:
        syllabus = await crud.get_syllabus(db, syllabus_id)
        if syllabus and syllabus.course_name:
            calendar_name = f"{syllabus.course_name} Assignments"

    ics_content = create_ics_calendar(assignments, calendar_name)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=assignments.ics"}
    )


@router.get("/json")
async def export_json(
    syllabus_id: Optional[int] = Query(None, description="Filter by syllabus"),
    db: AsyncSession = Depends(get_db)
):
    """Export assignments as JSON file."""
    assignments = await crud.get_all_assignments(db, syllabus_id)
    json_content = create_json_export(assignments)

    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=assignments.json"}
    )


@router.get("/csv")
async def export_csv(
    syllabus_id: Optional[int] = Query(None, description="Filter by syllabus"),
    db: AsyncSession = Depends(get_db)
):
    """Export assignments as CSV file."""
    assignments = await crud.get_all_assignments(db, syllabus_id)
    csv_content = create_csv_export(assignments)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assignments.csv"}
    )
