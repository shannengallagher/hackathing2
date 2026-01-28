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

        system_msg, user_msg = self._build_chat_messages(syllabus_text)

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                # First try with JSON format
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": user_msg}
                        ],
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                raw_response = result.get("message", {}).get("content", "")

                # If JSON format gives empty response, retry without it
                if len(raw_response.strip()) < 50:
                    print("[OLLAMA] JSON format gave minimal response, retrying without format constraint...", flush=True)
                    response = await client.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_msg},
                                {"role": "user", "content": user_msg}
                            ],
                            "stream": False
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    raw_response = result.get("message", {}).get("content", "")
            print(f"[OLLAMA] Raw response length: {len(raw_response)} chars", flush=True)
            print(f"[OLLAMA] Full raw response: {raw_response}", flush=True)

            # Check for empty or near-empty responses
            if len(raw_response.strip()) < 30:
                print(f"[OLLAMA] ERROR: Model returned empty/minimal response after retry.", flush=True)
                print(f"[OLLAMA] Response was: '{raw_response}'", flush=True)
                raise RuntimeError("Model returned empty response - the syllabus may be too complex")

            parsed = self._parse_response(raw_response)
            print(f"[OLLAMA] Parsed {len(parsed.get('assignments', []))} assignments from response", flush=True)

            processed = self._process_assignments(parsed)
            print(f"[OLLAMA] After processing: {len(processed.get('assignments', []))} assignments", flush=True)
            return processed

        except httpx.ConnectError:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is running: 'ollama serve'"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama API error: {e.response.status_code}")

    # Items to exclude (not real assignments)
    EXCLUDE_KEYWORDS = ["participation", "attendance", "class participation", "class attendance"]

    def _build_chat_messages(self, syllabus_text: str) -> tuple:
        """Build system and user messages for chat API."""

        system_msg = """List all assignments from a syllabus. Return JSON with assignment titles only.

Example:
{"course_name":"CS101","assignments":["Homework 1","Homework 2","Midterm Exam","Final Project","Quiz 1","Reading Chapter 1"]}

Rules:
- List EVERY assignment, homework, quiz, exam, project, paper, reading, presentation
- Do NOT include attendance or participation
- Output ONLY the JSON object"""

        user_msg = f"""List all assignments from this syllabus:

{syllabus_text[:12000]}"""

        return system_msg, user_msg

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the LLM response."""
        default_response = {"assignments": [], "course_info": {}}

        def normalize_structure(data: dict) -> dict:
            """Convert alternative structures to expected format."""
            if not isinstance(data, dict):
                return default_response

            result = {"assignments": [], "course_info": {}}

            # Extract course name from various possible locations
            course_name = data.get("course_name") or data.get("course_info", {}).get("course_name")
            result["course_info"] = {"course_name": course_name}

            # Get assignments list
            assignments = data.get("assignments", [])
            if not isinstance(assignments, list):
                assignments = []

            # Convert each assignment - handle both strings and dicts
            for item in assignments:
                if isinstance(item, str):
                    # Simple string title - determine type from keywords
                    title = item.strip()
                    title_lower = title.lower()

                    if "quiz" in title_lower:
                        atype = "quiz"
                    elif "exam" in title_lower or "midterm" in title_lower or "final" in title_lower:
                        atype = "exam"
                    elif "project" in title_lower:
                        atype = "project"
                    elif "paper" in title_lower or "essay" in title_lower or "report" in title_lower:
                        atype = "paper"
                    elif "reading" in title_lower or "chapter" in title_lower:
                        atype = "reading"
                    elif "presentation" in title_lower:
                        atype = "presentation"
                    elif "lab" in title_lower:
                        atype = "lab"
                    elif "homework" in title_lower or "hw" in title_lower or "assignment" in title_lower:
                        atype = "homework"
                    else:
                        atype = "other"

                    result["assignments"].append({
                        "title": title,
                        "type": atype,
                        "due_date": None,
                        "estimated_hours": None
                    })
                elif isinstance(item, dict):
                    # Already a dict - use as is
                    result["assignments"].append(item)

            print(f"[OLLAMA] Normalized structure, found {len(result['assignments'])} assignments", flush=True)
            return result

        try:
            data = json.loads(response_text)

            # Ensure we got a dict, not a string or other type
            if not isinstance(data, dict):
                print(f"[OLLAMA] Warning: Ollama returned non-dict type: {type(data)}", flush=True)
                return default_response

            return normalize_structure(data)

        except json.JSONDecodeError as e:
            print(f"[OLLAMA] JSON decode error: {e}", flush=True)

            # Try to fix common JSON issues
            cleaned = response_text.strip()

            # Remove trailing whitespace/newlines
            cleaned = re.sub(r'\s+$', '', cleaned)

            # Try to find the last complete JSON object
            try:
                # Find balanced braces
                brace_count = 0
                last_valid_end = -1
                for i, char in enumerate(cleaned):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            last_valid_end = i + 1

                if last_valid_end > 0:
                    truncated = cleaned[:last_valid_end]
                    data = json.loads(truncated)
                    if isinstance(data, dict):
                        print(f"[OLLAMA] Recovered JSON by truncating at position {last_valid_end}", flush=True)
                        return normalize_structure(data)
            except json.JSONDecodeError:
                pass

            # Attempt to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    if isinstance(parsed, dict):
                        return normalize_structure(parsed)
                except json.JSONDecodeError:
                    pass

            print(f"[OLLAMA] Warning: Could not parse Ollama response as JSON", flush=True)
            return default_response

    def _process_assignments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate extracted assignments."""
        processed_assignments = []

        # Ensure assignments is a list
        assignments = data.get("assignments", [])
        if not isinstance(assignments, list):
            print(f"[OLLAMA] Warning: assignments is not a list: {type(assignments)}", flush=True)
            assignments = []

        # Ensure course_info is a dict
        course_info = data.get("course_info", {})
        if not isinstance(course_info, dict):
            print(f"[OLLAMA] Warning: course_info is not a dict: {type(course_info)}", flush=True)
            course_info = {}

        print(f"[OLLAMA] Processing {len(assignments)} raw assignments", flush=True)

        for i, assignment in enumerate(assignments):
            # Skip if assignment is not a dict
            if not isinstance(assignment, dict):
                continue

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

            # Force quiz type if title contains "quiz" (ensures no time estimate)
            if "quiz" in title:
                assignment_type = "quiz"

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
            "course_info": course_info,
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
