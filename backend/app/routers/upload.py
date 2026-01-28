from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import uuid
import asyncio
import sys

from app.db.database import get_db, async_session
from app.db import crud
from app.models.assignment import Syllabus, SyllabusCreate
from app.services.parser import parser
from app.services.ollama_extractor import ollama_extractor
from app.config import settings

router = APIRouter()

# Store mapping of syllabus_id to file path
syllabus_files: dict[int, Path] = {}


def process_syllabus_sync(syllabus_id: int, file_path: Path):
    """Background task wrapper that creates its own event loop and db session."""
    print(f"[SYNC] Background task started for syllabus {syllabus_id}", flush=True)
    try:
        asyncio.run(_process_syllabus(syllabus_id, file_path))
    except Exception as e:
        print(f"[SYNC] Background task failed: {e}", flush=True)
        import traceback
        traceback.print_exc()


async def _process_syllabus(syllabus_id: int, file_path: Path):
    """Background task to process uploaded syllabus."""
    print(f"[BG] Starting processing for syllabus {syllabus_id}", flush=True)
    async with async_session() as db:
        try:
            # Parse document
            raw_text = parser.parse(file_path)
            print(f"[BG] Parsed document, got {len(raw_text)} characters", flush=True)

            # Extract assignments using Ollama
            print("[BG] Calling Ollama...", flush=True)
            extraction_result = await ollama_extractor.extract_assignments(raw_text)
            print(f"[BG] Ollama returned {len(extraction_result.get('assignments', []))} assignments", flush=True)

            # Get course info (with type safety)
            course_info = extraction_result.get("course_info", {})
            if not isinstance(course_info, dict):
                print(f"[BG] Warning: course_info is not a dict, using empty dict", flush=True)
                course_info = {}

            # Create assignments in database
            assignments = extraction_result.get("assignments", [])
            if not isinstance(assignments, list):
                print(f"[BG] Warning: assignments is not a list, using empty list", flush=True)
                assignments = []

            for assignment_data in assignments:
                if not isinstance(assignment_data, dict):
                    print(f"[BG] Warning: skipping non-dict assignment_data", flush=True)
                    continue
                assignment_data["course_name"] = course_info.get("course_name")
                await crud.create_assignment(db, syllabus_id, assignment_data)

            # Update syllabus status
            await crud.update_syllabus_status(
                db, syllabus_id, "completed",
                course_name=course_info.get("course_name"),
                instructor=course_info.get("instructor"),
                semester=course_info.get("semester")
            )
            print(f"[BG] Processing complete for syllabus {syllabus_id}", flush=True)

        except Exception as e:
            print(f"[BG] Error processing syllabus: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await crud.update_syllabus_status(db, syllabus_id, f"failed: {str(e)}")

        finally:
            # Clean up uploaded file
            if file_path.exists():
                file_path.unlink()


@router.post("/syllabus")
async def upload_syllabus(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a syllabus file for processing."""

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Use: {', '.join(settings.allowed_extensions)}"
        )

    # Save file temporarily
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = settings.upload_dir / unique_filename

    settings.upload_dir.mkdir(exist_ok=True)

    try:
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        with open(file_path, "wb") as f:
            f.write(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create syllabus record
    syllabus_data = SyllabusCreate(filename=file.filename)
    db_syllabus = await crud.create_syllabus(db, syllabus_data)

    # Process in background
    print(f"[UPLOAD] Adding background task for syllabus {db_syllabus.id}", flush=True)
    background_tasks.add_task(process_syllabus_sync, db_syllabus.id, file_path)

    return {
        "id": db_syllabus.id,
        "filename": db_syllabus.filename,
        "processing_status": db_syllabus.processing_status,
        "upload_date": db_syllabus.upload_date.isoformat() if db_syllabus.upload_date else None
    }


@router.get("/status/{syllabus_id}")
async def get_upload_status(syllabus_id: int, db: AsyncSession = Depends(get_db)):
    """Check the processing status of an uploaded syllabus."""
    syllabus = await crud.get_syllabus(db, syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    return {
        "id": syllabus.id,
        "filename": syllabus.filename,
        "status": syllabus.processing_status,
        "course_name": syllabus.course_name,
        "instructor": syllabus.instructor,
        "assignment_count": len(syllabus.assignments)
    }


@router.get("/history", response_model=list[Syllabus])
async def get_upload_history(db: AsyncSession = Depends(get_db)):
    """Get all uploaded syllabi."""
    return await crud.get_all_syllabi(db)


@router.delete("/{syllabus_id}")
async def delete_syllabus(syllabus_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a syllabus and its assignments."""
    success = await crud.delete_syllabus(db, syllabus_id)
    if not success:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return {"message": "Syllabus deleted successfully"}
