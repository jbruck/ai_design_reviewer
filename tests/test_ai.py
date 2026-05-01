from dfm_reviewer.ai import DisabledAIProvider, ReviewAIProvider


def test_disabled_ai_provider_returns_clear_message() -> None:
    provider: ReviewAIProvider = DisabledAIProvider()

    result = provider.suggest_open_questions(extracted_text="MATERIAL: 316 SS", context="machined")

    assert result == [
        "AI suggestions are disabled. Capture reviewer questions manually for this review."
    ]
