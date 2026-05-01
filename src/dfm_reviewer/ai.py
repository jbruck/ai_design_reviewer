from typing import Protocol


class ReviewAIProvider(Protocol):
    def suggest_open_questions(self, extracted_text: str, context: str) -> list[str]:
        """Suggest clarification questions from drawing text and review context."""


class DisabledAIProvider:
    def suggest_open_questions(self, extracted_text: str, context: str) -> list[str]:
        return [
            "AI suggestions are disabled. Capture reviewer questions manually for this review."
        ]
