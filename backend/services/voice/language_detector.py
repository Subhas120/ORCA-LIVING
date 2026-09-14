"""M4 Language Detection module.

Detects the language of recognized text using langdetect.
Falls back to a test provider when langdetect is unavailable.

SAFETY: Language detection is a pure linguistic operation.
It MUST NOT filter, interpret, or alter the content of text.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LanguageDetectionResult:
    """Result of language detection."""
    language_code: str
    confidence: float
    provider: str = "unknown"


class LanguageDetectionError(Exception):
    """Raised when language detection fails."""
    pass


class LanguageDetector(ABC):
    """Abstract interface for language detection."""

    @abstractmethod
    def detect(self, text: str) -> LanguageDetectionResult:
        """Detect the language of the given text.

        Args:
            text: Text to analyze.

        Returns:
            LanguageDetectionResult with language code and confidence.

        Raises:
            LanguageDetectionError: On detection failure.
        """


class LangdetectDetector(LanguageDetector):
    """Language detection using the langdetect library.

    langdetect is based on Google's language-detection library
    and supports 55 languages. It works fully offline.
    """

    SUPPORTED_LANGUAGES = {
        "en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu", "pa",
        "or", "ur", "fr", "de", "es", "pt", "it", "nl", "ru", "zh-cn",
        "zh-tw", "ja", "ko", "ar", "th", "vi", "id", "ms", "tl",
    }

    def __init__(self):
        try:
            from langdetect import detect_langs as _detect_langs
            self._detect_langs = _detect_langs
        except ImportError:
            raise LanguageDetectionError(
                "langdetect library not installed. "
                "Run: pip install langdetect"
            )

    def detect(self, text: str) -> LanguageDetectionResult:
        """Detect language using langdetect."""
        if not text or not text.strip():
            raise LanguageDetectionError("Cannot detect language of empty text")

        try:
            results = self._detect_langs(text)
            if not results:
                raise LanguageDetectionError("langdetect returned no results")

            top = results[0]
            return LanguageDetectionResult(
                language_code=str(top.lang),
                confidence=round(float(top.prob), 4),
                provider="langdetect"
            )
        except Exception as e:
            if isinstance(e, LanguageDetectionError):
                raise
            raise LanguageDetectionError(f"Language detection failed: {e}")


class TestLanguageDetector(LanguageDetector):
    """Deterministic language detector for testing."""

    def __init__(self, default_language: str = "en", default_confidence: float = 0.99):
        self._default_language = default_language
        self._default_confidence = default_confidence
        self._text_responses: dict[str, tuple[str, float]] = {}

    def set_response(self, text: str, language: str, confidence: float = 0.99):
        """Pre-configure a detection result for specific text."""
        self._text_responses[text] = (language, confidence)

    def detect(self, text: str) -> LanguageDetectionResult:
        """Return deterministic detection result."""
        if not text or not text.strip():
            raise LanguageDetectionError("Cannot detect language of empty text")

        if text in self._text_responses:
            lang, conf = self._text_responses[text]
            return LanguageDetectionResult(
                language_code=lang,
                confidence=conf,
                provider="test"
            )

        return LanguageDetectionResult(
            language_code=self._default_language,
            confidence=self._default_confidence,
            provider="test"
        )


def get_language_detector() -> LanguageDetector:
    """Factory: get the configured language detector.

    Controlled by ORCA_LANG_DETECTOR env var:
      - "langdetect" (default): langdetect library
      - "test": Deterministic test detector
    """
    provider_name = os.environ.get("ORCA_LANG_DETECTOR", "langdetect")

    if provider_name == "test":
        return TestLanguageDetector()
    elif provider_name == "langdetect":
        return LangdetectDetector()
    else:
        raise LanguageDetectionError(f"Unknown language detector: {provider_name}")
