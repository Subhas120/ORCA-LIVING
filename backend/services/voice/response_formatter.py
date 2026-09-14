"""M4 Response Formatter for Voice Output.

Converts a structured DecisionResponse into a human-readable
text suitable for text-to-speech synthesis.

SAFETY INVARIANT: This formatter MUST NOT:
  - alter the safety status (UNSAFE must remain UNSAFE)
  - paraphrase warnings to sound safer
  - remove uncertainty information
  - omit failed constraints
  - change numerical values, coordinates, or units
  - convert INSUFFICIENT_EVIDENCE into a positive recommendation
  - invent information not present in the response
"""

from __future__ import annotations

from backend.models.response import DecisionResponse, StatusEnum


class ResponseFormatter:
    """Formats DecisionResponse into speakable text.

    Preserves all safety-critical information. Numbers and coordinates
    are spoken as-is without alteration.
    """

    @staticmethod
    def format_for_speech(response: DecisionResponse, language: str = "en") -> str:
        """Convert a DecisionResponse to human-readable text.

        The output preserves the exact safety status, all warnings,
        and numerical values. It does NOT paraphrase unsafe results
        into safer-sounding language.

        Args:
            response: The M4 DecisionResponse.
            language: Target language code (formatting only, not translation).

        Returns:
            Formatted text string for TTS input.
        """
        status = response.status

        if status == StatusEnum.SERVICE_UNAVAILABLE:
            return (
                "The marine data service is currently unavailable. "
                "Please try again later. "
                "Do not proceed without a valid safety assessment."
            )

        if status == StatusEnum.INSUFFICIENT_EVIDENCE:
            summary = response.decisionSummary or "Insufficient scientific evidence for a safety assessment"
            return (
                f"Warning: Insufficient evidence for a safety decision. "
                f"{summary}. "
                f"Do not proceed without a valid safety assessment."
            )

        if status == StatusEnum.NO_SAFE_CANDIDATES:
            summary = response.decisionSummary or "No safe options were identified"
            parts = [
                f"Safety result: No safe candidates found. {summary}."
            ]

            # Include rejected candidates if available
            if response.rejectedCandidates:
                for candidate in response.rejectedCandidates:
                    reason = candidate.reason or "safety constraint violated"
                    parts.append(
                        f"Candidate {candidate.name} at coordinates "
                        f"{candidate.lat}, {candidate.lng} was rejected: {reason}."
                    )

            parts.append("It is not safe to proceed. Please wait for conditions to improve.")
            return " ".join(parts)

        if status == StatusEnum.DECISION_AVAILABLE:
            parts = []

            # Recommendation
            if response.recommendedCandidate:
                c = response.recommendedCandidate
                parts.append(
                    f"Recommended: {c.name} at coordinates "
                    f"{c.lat}, {c.lng}. Status: {c.status}."
                )
                if c.reason:
                    parts.append(f"Reason: {c.reason}.")

            # Summary
            if response.decisionSummary:
                parts.append(response.decisionSummary)

            # Tradeoffs
            if response.tradeoffs:
                parts.append("Tradeoffs: " + "; ".join(response.tradeoffs) + ".")

            # Uncertainty
            if response.uncertainty:
                parts.append(
                    f"Uncertainty level: {response.uncertainty.level}. "
                    f"{response.uncertainty.explanation}."
                )

            # Evidence
            if response.evidence:
                parts.append(f"Based on {len(response.evidence)} evidence items.")

            # Alternatives
            if response.alternativeCandidates:
                alt_names = [c.name for c in response.alternativeCandidates]
                parts.append(f"Alternatives considered: {', '.join(alt_names)}.")

            if not parts:
                parts.append("A decision is available. Please check detailed results.")

            return " ".join(parts)

        # Fallback — should never happen
        return f"Decision status: {status.value}. {response.decisionSummary or ''}"
