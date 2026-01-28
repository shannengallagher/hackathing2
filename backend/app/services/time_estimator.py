from typing import Optional
import re


class TimeEstimator:
    """Estimate time to complete assignments based on type and complexity."""

    # Types that don't need time estimates (in-class or attendance-based)
    NO_TIME_TYPES = {"quiz", "participation", "attendance", "discussion"}

    # Keywords that indicate no prep time needed
    NO_TIME_KEYWORDS = ["participation", "attendance", "in-class", "in class", "quiz"]

    # Base hours by assignment type
    BASE_HOURS = {
        "homework": 2.0,
        "quiz": 0,  # In-class, no prep time
        "exam": 4.0,  # Study time
        "midterm": 8.0,
        "final": 12.0,
        "project": 10.0,
        "paper": 8.0,
        "reading": 1.5,
        "presentation": 4.0,
        "lab": 3.0,
        "discussion": 0,  # In-class participation
        "participation": 0,
        "attendance": 0,
        "other": 2.0
    }

    # Keywords that modify estimated time
    COMPLEXITY_MULTIPLIERS = {
        # High complexity (increase time)
        "research": 1.5,
        "analysis": 1.3,
        "comprehensive": 1.5,
        "final": 1.5,
        "midterm": 1.3,
        "group": 1.2,
        "team": 1.2,
        "major": 1.4,

        # Lower complexity (decrease time)
        "short": 0.7,
        "brief": 0.7,
        "mini": 0.5,
        "quick": 0.6,
        "review": 0.8,
        "draft": 0.6,
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
        2. LLM estimate (if provided and reasonable)
        3. Length-based calculation (if patterns found)
        4. Type + complexity calculation
        """
        combined_text = f"{title} {description or ''}".lower()

        # Check if this type doesn't need a time estimate
        if assignment_type.lower() in self.NO_TIME_TYPES:
            return None

        # Check for keywords indicating no prep time
        for keyword in self.NO_TIME_KEYWORDS:
            if keyword in combined_text:
                return None

        # Use LLM estimate if provided and reasonable (0.25 to 50 hours)
        if llm_estimate and 0.25 <= llm_estimate <= 50:
            return round(llm_estimate, 2)

        # Try length-based estimation first
        length_estimate = self._estimate_from_length(combined_text)
        if length_estimate:
            return round(max(0.25, min(length_estimate, 40.0)), 2)

        # Fall back to type + complexity
        base = self.BASE_HOURS.get(assignment_type.lower(), 2.0)
        multiplier = self._calculate_complexity_multiplier(combined_text)

        estimate = base * multiplier

        # Clamp to reasonable range
        return round(max(0.25, min(estimate, 40.0)), 2)

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
