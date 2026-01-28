from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from app.db.database import get_db
from app.db import crud
from app.models.assignment import Assignment, AssignmentCreate, AssignmentUpdate, AssignmentType

router = APIRouter()


@router.get("", response_model=List[Assignment])
async def get_assignments(
    syllabus_id: Optional[int] = Query(None, description="Filter by syllabus"),
    assignment_type: Optional[str] = Query(None, description="Filter by type"),
    db: AsyncSession = Depends(get_db)
):
    """Get all assignments with optional filters."""
    assignments = await crud.get_all_assignments(db, syllabus_id)

    # Filter by type if specified
    if assignment_type:
        assignments = [a for a in assignments if a.assignment_type == assignment_type]

    return assignments


@router.get("/upcoming", response_model=List[Assignment])
async def get_upcoming_assignments(
    days: int = Query(14, ge=1, le=365, description="Number of days ahead"),
    db: AsyncSession = Depends(get_db)
):
    """Get assignments due in the next N days."""
    return await crud.get_upcoming_assignments(db, days)


@router.get("/stats")
async def get_assignment_stats(db: AsyncSession = Depends(get_db)):
    """Get summary statistics for all assignments."""
    assignments = await crud.get_all_assignments(db)
    today = date.today()

    total = len(assignments)
    upcoming = sum(1 for a in assignments if a.due_date and a.due_date >= today)
    overdue = sum(1 for a in assignments if a.due_date and a.due_date < today)
    total_hours = sum(a.estimated_hours or 0 for a in assignments)

    # Count by type
    by_type = {}
    for a in assignments:
        t = a.assignment_type or "other"
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total": total,
        "upcoming": upcoming,
        "overdue": overdue,
        "total_hours": round(total_hours, 1),
        "by_type": by_type
    }


@router.get("/{assignment_id}", response_model=Assignment)
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single assignment by ID."""
    assignment = await crud.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: int,
    update_data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing assignment.

    If estimated_hours is being updated, also updates all assignments
    with the same title in the same syllabus.
    """
    # Only include fields that were actually provided
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

    # First, get the assignment to check if we need batch update
    assignment = await crud.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # If updating estimated_hours, update all assignments with same title
    if "estimated_hours" in update_dict:
        await crud.update_assignments_by_title(
            db,
            assignment.syllabus_id,
            assignment.title,
            {"estimated_hours": update_dict["estimated_hours"]}
        )

    # Update the specific assignment with all fields
    assignment = await crud.update_assignment(db, assignment_id, update_dict)
    return assignment


@router.post("/fix-quiz-times")
async def fix_quiz_times(db: AsyncSession = Depends(get_db)):
    """Clear time estimates for all quiz assignments."""
    count = await crud.clear_quiz_time_estimates(db)
    return {"message": f"Cleared time estimates for {count} quiz assignments"}


@router.delete("/{assignment_id}")
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an assignment."""
    success = await crud.delete_assignment(db, assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"message": "Assignment deleted successfully"}
