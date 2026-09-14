"""Comprehensive voice pipeline tests for M4.

Tests cover all 8 required test scenarios:
  1. English E2E
  2. Non-English (Hindi) E2E
  3. Ambiguous input → CLARIFICATION_REQUIRED
  4. M2 unavailable → SERVICE_UNAVAILABLE
  5. M2 insufficient evidence → INSUFFICIENT_EVIDENCE
  6. No safe candidates → NO_SAFE_CANDIDATES
  7. Safe decision → DECISION_AVAILABLE preserved through voice
  8. Unsafe decision → UNSAFE preserved through voice

All tests use deterministic test providers (STT, TTS, language
detector, translation) so they work offline without network access.

SAFETY: Tests verify that safety statuses are NEVER altered
by the voice layer.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from backend.main import app

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.voice.stt_provider import TestSTTProvider, STTResult
from backend.services.voice.language_detector import TestLanguageDetector, LanguageDetectionResult
from backend.services.voice.translation_provider import TestTranslationProvider
from backend.services.voice.tts_provider import TestTTSProvider
from backend.services.voice.intent_extractor import (
    extract_intent, ExtractedIntent, ClarificationRequired,
)
from backend.services.voice.response_formatter import ResponseFormatter
from backend.services.voice.voice_pipeline import VoicePipeline, VoiceResponse


client = TestClient(app)


# ============================================================
# Unit Tests: Individual Components
# ============================================================

class TestSTTProviderUnit:
    """Test the deterministic STT provider."""

    def test_recognize_returns_default(self):
        provider = TestSTTProvider()
        result = provider.recognize(b"fake_audio")
        assert result.text == "Find safe fishing near Kochi tomorrow morning"
        assert result.confidence == 1.0
        assert result.provider == "test"

    def test_recognize_file_returns_custom(self):
        provider = TestSTTProvider()
        provider.set_response("test.wav", "Diving near Mumbai")
        result = provider.recognize_file("test.wav")
        assert result.text == "Diving near Mumbai"

    def test_recognize_file_returns_default(self):
        provider = TestSTTProvider()
        result = provider.recognize_file("unknown.wav")
        assert result.text == "Find safe fishing near Kochi tomorrow morning"


class TestLanguageDetectorUnit:
    """Test the deterministic language detector."""

    def test_detect_default_english(self):
        detector = TestLanguageDetector()
        result = detector.detect("hello world")
        assert result.language_code == "en"
        assert result.confidence >= 0.9

    def test_detect_custom_language(self):
        detector = TestLanguageDetector()
        detector.set_response("मछली पकड़ना", "hi", 0.95)
        result = detector.detect("मछली पकड़ना")
        assert result.language_code == "hi"
        assert result.confidence == 0.95


class TestIntentExtractor:
    """Test intent extraction from normalized text."""

    def test_complete_english_input(self):
        result = extract_intent("Find safe fishing near Kochi tomorrow morning")
        assert isinstance(result, ExtractedIntent)
        assert result.activity == "fishing"
        assert result.location == "Kochi"
        assert result.date == "tomorrow"
        assert result.time == "morning"

    def test_missing_activity(self):
        result = extract_intent("near Kochi tomorrow")
        assert isinstance(result, ClarificationRequired)
        assert "activity" in result.missing_fields

    def test_missing_location(self):
        result = extract_intent("fishing tomorrow morning")
        assert isinstance(result, ClarificationRequired)
        assert "location" in result.missing_fields

    def test_missing_both(self):
        result = extract_intent("what should I do")
        assert isinstance(result, ClarificationRequired)
        assert "activity" in result.missing_fields
        assert "location" in result.missing_fields

    def test_empty_input(self):
        result = extract_intent("")
        assert isinstance(result, ClarificationRequired)
        assert "query" in result.missing_fields

    def test_vessel_type_extraction(self):
        result = extract_intent(
            "small boat fishing near Kochi tomorrow morning"
        )
        assert isinstance(result, ExtractedIntent)
        assert result.vessel_type == "Small"

    def test_diving_activity(self):
        result = extract_intent("diving near Goa tomorrow morning")
        assert isinstance(result, ExtractedIntent)
        assert result.activity == "diving"
        assert result.location == "Goa"

class TestResponseFormatter:
    """Test that response formatter preserves safety statuses."""

    def test_service_unavailable(self):
        response = DecisionResponse(status=StatusEnum.SERVICE_UNAVAILABLE)
        text = ResponseFormatter.format_for_speech(response)
        assert "unavailable" in text.lower()
        assert "do not proceed" in text.lower()

    def test_insufficient_evidence(self):
        response = DecisionResponse(
            status=StatusEnum.INSUFFICIENT_EVIDENCE,
            decisionSummary="M2 lacks safety data"
        )
        text = ResponseFormatter.format_for_speech(response)
        assert "insufficient evidence" in text.lower()
        assert "do not proceed" in text.lower()

    def test_no_safe_candidates(self):
        response = DecisionResponse(
            status=StatusEnum.NO_SAFE_CANDIDATES,
            decisionSummary="All candidates failed safety checks"
        )
        text = ResponseFormatter.format_for_speech(response)
        assert "no safe candidates" in text.lower()
        assert "not safe to proceed" in text.lower()

    def test_decision_available(self):
        response = DecisionResponse(
            status=StatusEnum.DECISION_AVAILABLE,
            decisionSummary="Safe fishing available"
        )
        text = ResponseFormatter.format_for_speech(response)
        assert "safe fishing available" in text.lower()


class TestTranslationProviderUnit:
    """Test the deterministic translation provider."""

    def test_same_language_passthrough(self):
        provider = TestTranslationProvider()
        result = provider.translate("hello", "en", "en")
        assert result.translated_text == "hello"

    def test_known_hindi_to_english(self):
        provider = TestTranslationProvider()
        result = provider.translate(
            "कल सुबह मछली पकड़ना", "hi", "en"
        )
        assert result.translated_text == "Fishing tomorrow morning"

    def test_unknown_text_prefixed(self):
        provider = TestTranslationProvider()
        result = provider.translate("unknown text", "en", "hi")
        assert result.translated_text == "[hi] unknown text"


class TestTTSProviderUnit:
    """Test the deterministic TTS provider."""

    def test_synthesize_english(self):
        provider = TestTTSProvider()
        result = provider.synthesize("Hello world", "en")
        assert result.audio_bytes is not None
        assert len(result.audio_bytes) > 0
        assert result.provider == "test"

    def test_synthesize_hindi(self):
        provider = TestTTSProvider()
        result = provider.synthesize("Test text", "hi")
        assert result.audio_bytes is not None

    def test_unsupported_language(self):
        from backend.services.voice.tts_provider import TTSUnsupportedLanguageError
        provider = TestTTSProvider()
        with pytest.raises(TTSUnsupportedLanguageError):
            provider.synthesize("Test", "zz")


# ============================================================
# Integration Tests: Full Voice Pipeline
# ============================================================

def _make_test_pipeline(stt_text="Find safe fishing near Kochi tomorrow morning", lang="en"):
    """Create a voice pipeline with all test providers."""
    stt = TestSTTProvider(default_text=stt_text)
    detector = TestLanguageDetector(default_language=lang)
    translator = TestTranslationProvider()
    tts = TestTTSProvider()
    return VoicePipeline(stt=stt, language_detector=detector, translator=translator, tts=tts)


# Test 1 — English E2E
def test_voice_english_e2e():
    """English audio → English objective → M4 → English response → English TTS."""
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        assert request.activity == "fishing"
        assert request.location == "Kochi"
        return DecisionResponse(
            status=StatusEnum.INSUFFICIENT_EVIDENCE,
            decisionSummary="M2 lacks safety capability"
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert result.language == "en"
    assert result.transcript == "Find safe fishing near Kochi tomorrow morning"
    assert "insufficient evidence" in result.response_text.lower()
    assert result.audio_base64 is not None


# Test 2 — Non-English (Hindi) E2E
def test_voice_hindi_e2e():
    """Hindi text → detect Hindi → translate → objective → M4 → translate response → Hindi TTS."""
    stt = TestSTTProvider(default_text="कल सुबह मछली पकड़ना")
    detector = TestLanguageDetector(default_language="hi")
    translator = TestTranslationProvider()
    tts = TestTTSProvider()
    pipeline = VoicePipeline(stt=stt, language_detector=detector, translator=translator, tts=tts)

    # Hindi text translates to "Fishing tomorrow morning" which has no location → clarification
    result = pipeline.process_audio_bytes(b"fake_audio", lambda r: None)
    assert result.status == "CLARIFICATION_REQUIRED"
    assert result.language == "hi"
    assert "मछली" in result.transcript


# Test 3 — Ambiguous input → CLARIFICATION_REQUIRED
def test_voice_ambiguous_input():
    """Ambiguous text → CLARIFICATION_REQUIRED instead of guessing."""
    pipeline = _make_test_pipeline(
        stt_text="what should I do",
        lang="en"
    )

    result = pipeline.process_audio_bytes(b"fake_audio", lambda r: None)
    assert result.status == "CLARIFICATION_REQUIRED"
    assert result.missing_fields is not None
    assert "activity" in result.missing_fields


# Test 4 — M2 unavailable → SERVICE_UNAVAILABLE
def test_voice_m2_unavailable():
    """M2 returns SERVICE_UNAVAILABLE → voice preserves it."""
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            status=StatusEnum.SERVICE_UNAVAILABLE,
            decisionSummary="M2 service down"
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)
    assert result.status == "SERVICE_UNAVAILABLE"
    assert "unavailable" in result.response_text.lower()


# Test 5 — M2 insufficient evidence → INSUFFICIENT_EVIDENCE
def test_voice_insufficient_evidence():
    """M2 insufficient evidence → voice preserves INSUFFICIENT_EVIDENCE."""
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            status=StatusEnum.INSUFFICIENT_EVIDENCE,
            decisionSummary="M2 lacks safety capability. Cannot generate valid SafetyEvaluation."
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert "insufficient evidence" in result.response_text.lower()
    assert "do not proceed" in result.response_text.lower()


# Test 6 — No safe candidates → NO_SAFE_CANDIDATES
def test_voice_no_safe_candidates():
    """M1 returns no safe candidates → voice preserves NO_SAFE_CANDIDATES."""
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            status=StatusEnum.NO_SAFE_CANDIDATES,
            decisionSummary="All candidates failed safety firewall"
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)
    assert result.status == "NO_SAFE_CANDIDATES"
    assert "no safe candidates" in result.response_text.lower()
    assert "not safe to proceed" in result.response_text.lower()


# Test 7 — Safe decision → DECISION_AVAILABLE preserved
def test_voice_safe_decision():
    """DECISION_AVAILABLE remains DECISION_AVAILABLE through voice."""
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            status=StatusEnum.DECISION_AVAILABLE,
            decisionSummary="Safe fishing area identified at 9.9°N 76.2°E"
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)
    assert result.status == "DECISION_AVAILABLE"
    assert result.decision is not None
    assert result.decision["status"] == "DECISION_AVAILABLE"
    assert result.audio_base64 is not None


# Test 8 — Safety preservation: unsafe must remain unsafe
def test_voice_safety_preservation_unsafe():
    """NO_SAFE_CANDIDATES (unsafe result) must NOT be altered by voice layer.

    This test verifies the critical safety invariant:
    Voice MUST NOT convert an unsafe decision into a safe-sounding one.
    """
    pipeline = _make_test_pipeline(
        stt_text="Find safe fishing near Kochi tomorrow morning",
        lang="en"
    )

    def mock_decision_handler(request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            status=StatusEnum.NO_SAFE_CANDIDATES,
            decisionSummary="DANGEROUS: wave height 4.2m exceeds 2.0m safety limit"
        )

    result = pipeline.process_audio_bytes(b"fake_audio", mock_decision_handler)

    # Safety status preserved
    assert result.status == "NO_SAFE_CANDIDATES"

    # The warning text must include the danger information
    assert "no safe candidates" in result.response_text.lower()
    assert "not safe to proceed" in result.response_text.lower()

    # Decision payload preserved
    assert result.decision is not None
    assert result.decision["status"] == "NO_SAFE_CANDIDATES"
    assert "DANGEROUS" in result.decision["decisionSummary"]


# ============================================================
# API Endpoint Tests
# ============================================================

def test_voice_text_endpoint():
    """Test POST /api/v1/voice/text with English input."""
    # Use test providers via env vars
    with patch.dict(os.environ, {
        "ORCA_STT_PROVIDER": "test",
        "ORCA_LANG_DETECTOR": "test",
        "ORCA_TRANSLATION_PROVIDER": "test",
        "ORCA_TTS_PROVIDER": "test",
    }):
        response = client.post(
            "/api/v1/voice/text",
            json={"text": "Find safe fishing near Kochi tomorrow morning"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert data["transcript"] == "Find safe fishing near Kochi tomorrow morning"
        # M2 currently returns INSUFFICIENT_EVIDENCE
        assert data["status"] in [
            "INSUFFICIENT_EVIDENCE", "SERVICE_UNAVAILABLE",
            "NO_SAFE_CANDIDATES", "DECISION_AVAILABLE"
        ]


def test_voice_text_endpoint_ambiguous():
    """Test POST /api/v1/voice/text with ambiguous input."""
    with patch.dict(os.environ, {
        "ORCA_STT_PROVIDER": "test",
        "ORCA_LANG_DETECTOR": "test",
        "ORCA_TRANSLATION_PROVIDER": "test",
        "ORCA_TTS_PROVIDER": "test",
    }):
        response = client.post(
            "/api/v1/voice/text",
            json={"text": "what should I do"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CLARIFICATION_REQUIRED"
        assert data["missing_fields"] is not None


def test_voice_endpoint_no_input():
    """Test POST /api/v1/voice with neither audio nor text."""
    response = client.post("/api/v1/voice")
    assert response.status_code == 400
