import httpx
import json
import re
from typing import Dict, Any, List
from app.config import settings
from app.services.time_estimator import time_estimator


class OllamaExtractor:
    """Extract assignments from syllabus text using Ollama."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def extract_assignments(self, syllabus_text: str) -> Dict[str, Any]:
        """Send text to Ollama and extract structured assignment data."""

        prompt = self._build_prompt(syllabus_text)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()

            parsed = self._parse_response(result.get("response", ""))
            return self._process_assignments(parsed)

        except httpx.ConnectError:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is running: 'ollama serve'"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama API error: {e.response.status_code}")

    # Items to exclude (not real assignments)
    EXCLUDE_KEYWORDS = ["participation", "attendance", "class participation", "class attendance"]

    def _build_prompt(self, syllabus_text: str) -> str:
        return f"""You are an expert at analyzing academic syllabi. Your job is to extract EVERY assignment, homework, quiz, exam, project, paper, reading, and deadline from the syllabus.

IMPORTANT INSTRUCTIONS:
- Extract ALL assignments, even small ones like weekly homeworks, reading assignments, or minor quizzes
- Look carefully at course schedules, weekly breakdowns, and assignment lists
- Include assignments mentioned in tables, bullet points, or inline text
- Do NOT include "class participation" or "attendance" - these are not assignments
- If there are numbered assignments (HW1, HW2, etc.), include each one separately
- If there's a weekly schedule with assignments, extract each week's assignments

For each item found, extract:
1. title: Specific name of the assignment (e.g., "Homework 1", "Midterm Exam", "Chapter 3 Reading")
2. type: One of [homework, quiz, exam, project, paper, reading, presentation, lab, other]
3. due_date: In YYYY-MM-DD format (use null if not specified)
4. due_time: In HH:MM format if specified (use null if not mentioned)
5. description: Brief description if available
6. weight: Grade percentage weight if mentioned (as decimal, e.g., 0.20 for 20%)
7. estimated_hours: Your estimate of time needed (float)

Also extract course information:
- course_name: Full course name/title
- instructor: Professor/instructor name
- semester: Term/semester if mentioned

Respond ONLY with valid JSON:
{{
  "course_info": {{
    "course_name": "string or null",
    "instructor": "string or null",
    "semester": "string or null"
  }},
  "assignments": [
    {{
      "title": "string",
      "type": "string",
      "due_date": "YYYY-MM-DD or null",
      "due_time": "HH:MM or null",
      "description": "string or null",
      "weight": 0.0,
      "estimated_hours": 2.0
    }}
  ]
}}

SYLLABUS TEXT:
{syllabus_text[:12000]}

JSON RESPONSE:"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the LLM response."""
        try:
            data = json.loads(response_text)

            if "assignments" not in data:
                data["assignments"] = []
            if "course_info" not in data:
                data["course_info"] = {}

            return data
        except json.JSONDecodeError:
            # Attempt to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            return {"assignments": [], "course_info": {}}

    def _process_assignments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate extracted assignments."""
        processed_assignments = []

        for assignment in data.get("assignments", []):
            if not assignment.get("title"):
                continue

            title = assignment.get("title", "").strip().lower()

            # Skip participation/attendance items
            if any(keyword in title for keyword in self.EXCLUDE_KEYWORDS):
                continue

            assignment_type = assignment.get("type", "other").lower()

            # Also skip if type is participation or attendance
            if assignment_type in ["participation", "attendance"]:
                continue

            if assignment_type not in ["homework", "quiz", "exam", "project", "paper",
                                       "reading", "presentation", "lab", "other"]:
                assignment_type = "other"

            # Use time estimator to refine or fill in time estimates
            estimated_hours = time_estimator.estimate(
                assignment_type=assignment_type,
                title=assignment.get("title", ""),
                description=assignment.get("description"),
                llm_estimate=assignment.get("estimated_hours")
            )

            processed = {
                "title": assignment.get("title", "").strip(),
                "description": assignment.get("description"),
                "assignment_type": assignment_type,
                "due_date": self._parse_date(assignment.get("due_date")),
                "due_time": assignment.get("due_time"),
                "estimated_hours": estimated_hours,
                "weight_percentage": assignment.get("weight"),
                "confidence_score": 0.8  # Default confidence
            }

            processed_assignments.append(processed)

        return {
            "course_info": data.get("course_info", {}),
            "assignments": processed_assignments
        }

    def _parse_date(self, date_str: str) -> str:
        """Validate and return date string or None."""
        if not date_str or date_str == "null":
            return None

        # Basic validation for YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        return None


# Singleton instance
ollama_extractor = OllamaExtractor()
