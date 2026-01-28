from icalendar import Calendar, Event
from datetime import datetime, timedelta
from typing import List
import csv
import json
from io import StringIO

from app.db.models import AssignmentDB


def create_ics_calendar(assignments: List[AssignmentDB], calendar_name: str = "Syllabus Assignments") -> str:
    """Create an ICS calendar file from assignments."""
    cal = Calendar()
    cal.add('prodid', '-//Syllabus Parser//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', calendar_name)

    for assignment in assignments:
        if not assignment.due_date:
            continue

        event = Event()
        event.add('summary', assignment.title)

        # Set due date/time
        if assignment.due_time:
            try:
                hour, minute = map(int, assignment.due_time.split(':'))
                dt = datetime.combine(assignment.due_date, datetime.min.time().replace(hour=hour, minute=minute))
            except ValueError:
                dt = datetime.combine(assignment.due_date, datetime.min.time().replace(hour=23, minute=59))
        else:
            dt = datetime.combine(assignment.due_date, datetime.min.time().replace(hour=23, minute=59))

        event.add('dtstart', dt)
        event.add('dtend', dt + timedelta(hours=1))

        # Add description
        description_parts = []
        if assignment.description:
            description_parts.append(assignment.description)
        description_parts.append(f"Type: {assignment.assignment_type}")
        description_parts.append(f"Estimated time: {assignment.estimated_hours} hours")
        if assignment.weight_percentage:
            description_parts.append(f"Weight: {assignment.weight_percentage * 100}%")

        event.add('description', "\n".join(description_parts))

        # Add unique ID
        event.add('uid', f"assignment-{assignment.id}@syllabus-parser")

        cal.add_component(event)

    return cal.to_ical().decode('utf-8')


def create_json_export(assignments: List[AssignmentDB]) -> str:
    """Create a JSON export of assignments."""
    data = []
    for assignment in assignments:
        data.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "type": assignment.assignment_type,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "due_time": assignment.due_time,
            "estimated_hours": assignment.estimated_hours,
            "weight_percentage": assignment.weight_percentage,
            "course_name": assignment.course_name,
            "created_at": assignment.created_at.isoformat() if assignment.created_at else None
        })

    return json.dumps(data, indent=2)


def create_csv_export(assignments: List[AssignmentDB]) -> str:
    """Create a CSV export of assignments."""
    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "ID", "Title", "Description", "Type", "Due Date", "Due Time",
        "Estimated Hours", "Weight %", "Course Name"
    ])

    for assignment in assignments:
        writer.writerow([
            assignment.id,
            assignment.title,
            assignment.description or "",
            assignment.assignment_type,
            assignment.due_date.isoformat() if assignment.due_date else "",
            assignment.due_time or "",
            assignment.estimated_hours,
            assignment.weight_percentage * 100 if assignment.weight_percentage else "",
            assignment.course_name or ""
        ])

    return output.getvalue()
