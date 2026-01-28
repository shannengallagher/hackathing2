from typing import Optional
import re


class TimeEstimator:
    """Estimate time to complete assignments based on type and complexity."""

    # Types that don't need time estimates (in-class or attendance-based)
    NO_TIME_TYPES = {"quiz", "participation", "attendance", "discussion"}

    # Keywords that indicate no prep time needed
    NO_TIME_KEYWORDS = ["participation", "attendance", "in-class", "in class", "quiz"]

    # Base hours by assignment type (conservative estimates)
    BASE_HOURS = {
        "homework": 1.5,      # Typical weekly homework
        "quiz": 0,            # In-class, no prep time
        "exam": 3.0,          # Study time for regular exam
        "project": 8.0,       # Multi-week project
        "paper": 5.0,         # Standard paper/essay
        "reading": 1.0,       # Reading assignment
        "presentation": 3.0,  # Prepare slides + practice
        "lab": 2.0,           # Lab work + writeup
        "discussion": 0,      # In-class participation
        "participation": 0,
        "attendance": 0,
        "other": 1.0          # Default conservative
    }

    # Keywords that modify estimated time
    COMPLEXITY_MULTIPLIERS = {
        # High complexity (increase time)
        "research": 1.8,
        "analysis": 1.4,
        "comprehensive": 1.6,
        "final": 2.0,         # Final exams/projects need more time
        "midterm": 1.5,
        "group": 1.3,
        "team": 1.3,
        "major": 1.5,
        "term": 1.8,          # Term paper/project
        "capstone": 2.0,
        "thesis": 2.5,
        "essay": 1.2,
        "report": 1.3,

        # Lower complexity (decrease time)
        "short": 0.6,
        "brief": 0.6,
        "mini": 0.4,
        "quick": 0.5,
        "review": 0.7,
        "draft": 0.5,
        "rough": 0.5,
        "outline": 0.4,
        "weekly": 0.8,        # Weekly assignments are usually smaller
    }

    # Length patterns and their hour estimates
    LENGTH_PATTERNS = [
        (r'(\d+)\s*pages?', lambda x: int(x) * 0.5),       # 0.5 hrs per page
        (r'(\d+)\s*words?', lambda x: int(x) / 500),       # ~500 words/hr
        (r'(\d+)\s*problems?', lambda x: int(x) * 0.25),   # 15 min per problem
        (r'(\d+)\s*questions?', lambda x: int(x) * 0.15),  # 10 min per question
        (r'(\d+)\s*chapters?', lambda x: int(x) * 2.0),    # 2 hrs per chapter
        (r'(\d+)\s*exercises?', lambda x: int(x) * 0.2),   # 12 min per exercise
    ]

    def estimate(
        self,
        assignment_type: str,
        title: str,
        description: Optional[str] = None,
        llm_estimate: Optional[float] = None
    ) -> Optional[float]:
        """
        Estimate hours needed for an assignment.
        Returns None for items that don't need prep time (quizzes, participation, etc.)

        Priority:
        1. Check if type doesn't need time estimate
        2. Length-based calculation (if patterns found)
        3. Type + complexity calculation
        4. LLM estimate used only as sanity check
        """
        combined_text = f"{title} {description or ''}".lower()

        # Check if this type doesn't need a time estimate
        if assignment_type.lower() in self.NO_TIME_TYPES:
            return None

        # Check for keywords indicating no prep time
        for keyword in self.NO_TIME_KEYWORDS:
            if keyword in combined_text:
                return None

        # Try length-based estimation first (most accurate)
        length_estimate = self._estimate_from_length(combined_text)
        if length_estimate:
            return round(max(0.25, min(length_estimate, 40.0)), 1)

        # Calculate type + complexity estimate
        base = self.BASE_HOURS.get(assignment_type.lower(), 1.0)
        multiplier = self._calculate_complexity_multiplier(combined_text)
        calculated_estimate = base * multiplier

        # Clamp to reasonable range and round to nearest 0.5
        final = max(0.5, min(calculated_estimate, 40.0))
        return round(final * 2) / 2  # Round to nearest 0.5

    def _estimate_from_length(self, text: str) -> Optional[float]:
        """Extract time estimate from length specifications in text."""
        for pattern, calculator in self.LENGTH_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return calculator(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    def _calculate_complexity_multiplier(self, text: str) -> float:
        """Calculate multiplier based on complexity keywords."""
        multiplier = 1.0

        for keyword, factor in self.COMPLEXITY_MULTIPLIERS.items():
            if keyword in text:
                if factor > 1 and factor > multiplier:
                    multiplier = factor
                elif factor < 1 and factor < multiplier:
                    multiplier = factor

        return multiplier


# Singleton instance
time_estimator = TimeEstimator()
