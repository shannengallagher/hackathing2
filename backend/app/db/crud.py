from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, timedelta

from .models import SyllabusDB, AssignmentDB
from app.models.assignment import SyllabusCreate, AssignmentCreate


async def create_syllabus(db: AsyncSession, syllabus: SyllabusCreate) -> SyllabusDB:
    db_syllabus = SyllabusDB(
        filename=syllabus.filename,
        file_path=syllabus.file_path,
        course_name=syllabus.course_name,
        instructor=syllabus.instructor,
        semester=syllabus.semester,
        raw_text=syllabus.raw_text,
        processing_status="processing"
    )
    db.add(db_syllabus)
    await db.commit()
    await db.refresh(db_syllabus)
    return db_syllabus


async def get_syllabus(db: AsyncSession, syllabus_id: int) -> Optional[SyllabusDB]:
    result = await db.execute(
        select(SyllabusDB)
        .options(selectinload(SyllabusDB.assignments))
        .where(SyllabusDB.id == syllabus_id)
    )
    return result.scalar_one_or_none()


async def get_all_syllabi(db: AsyncSession) -> List[SyllabusDB]:
    result = await db.execute(
        select(SyllabusDB)
        .options(selectinload(SyllabusDB.assignments))
        .order_by(SyllabusDB.upload_date.desc())
    )
    return list(result.scalars().all())


async def update_syllabus_status(db: AsyncSession, syllabus_id: int, status: str, course_name: str = None, instructor: str = None, semester: str = None):
    syllabus = await get_syllabus(db, syllabus_id)
    if syllabus:
        syllabus.processing_status = status
        if course_name:
            syllabus.course_name = course_name
        if instructor:
            syllabus.instructor = instructor
        if semester:
            syllabus.semester = semester
        await db.commit()
    return syllabus


async def create_assignment(db: AsyncSession, syllabus_id: int, assignment_data: dict) -> AssignmentDB:
    db_assignment = AssignmentDB(
        syllabus_id=syllabus_id,
        **assignment_data
    )
    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)
    return db_assignment


async def get_assignment(db: AsyncSession, assignment_id: int) -> Optional[AssignmentDB]:
    result = await db.execute(
        select(AssignmentDB).where(AssignmentDB.id == assignment_id)
    )
    return result.scalar_one_or_none()


async def get_all_assignments(db: AsyncSession, syllabus_id: Optional[int] = None) -> List[AssignmentDB]:
    query = select(AssignmentDB).order_by(AssignmentDB.due_date.asc().nullslast())
    if syllabus_id:
        query = query.where(AssignmentDB.syllabus_id == syllabus_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_upcoming_assignments(db: AsyncSession, days: int = 14) -> List[AssignmentDB]:
    today = date.today()
    end_date = today + timedelta(days=days)
    result = await db.execute(
        select(AssignmentDB)
        .where(AssignmentDB.due_date >= today)
        .where(AssignmentDB.due_date <= end_date)
        .order_by(AssignmentDB.due_date.asc())
    )
    return list(result.scalars().all())


async def update_assignment(db: AsyncSession, assignment_id: int, update_data: dict) -> Optional[AssignmentDB]:
    assignment = await get_assignment(db, assignment_id)
    if assignment:
        for key, value in update_data.items():
            if hasattr(assignment, key) and value is not None:
                setattr(assignment, key, value)
        await db.commit()
        await db.refresh(assignment)
    return assignment


async def delete_assignment(db: AsyncSession, assignment_id: int) -> bool:
    result = await db.execute(
        delete(AssignmentDB).where(AssignmentDB.id == assignment_id)
    )
    await db.commit()
    return result.rowcount > 0


async def update_assignments_by_title(db: AsyncSession, syllabus_id: int, title: str, update_data: dict) -> List[AssignmentDB]:
    """Update all assignments with the same title in a syllabus."""
    result = await db.execute(
        select(AssignmentDB)
        .where(AssignmentDB.syllabus_id == syllabus_id)
        .where(AssignmentDB.title == title)
    )
    assignments = list(result.scalars().all())

    for assignment in assignments:
        for key, value in update_data.items():
            if hasattr(assignment, key) and value is not None:
                setattr(assignment, key, value)

    await db.commit()

    # Refresh all assignments to get updated values
    for assignment in assignments:
        await db.refresh(assignment)

    return assignments


async def clear_quiz_time_estimates(db: AsyncSession) -> int:
    """Clear time estimates for all quiz assignments."""
    result = await db.execute(
        select(AssignmentDB).where(
            or_(
                AssignmentDB.assignment_type == "quiz",
                AssignmentDB.title.ilike("%quiz%")
            )
        )
    )
    assignments = list(result.scalars().all())

    count = 0
    for assignment in assignments:
        if assignment.estimated_hours is not None:
            assignment.estimated_hours = None
            count += 1

    await db.commit()
    return count


async def delete_syllabus(db: AsyncSession, syllabus_id: int) -> bool:
    # Use ORM delete to trigger cascade delete of assignments
    syllabus = await get_syllabus(db, syllabus_id)
    if syllabus:
        await db.delete(syllabus)
        await db.commit()
        return True
    return False
