"""M4 Translation module.

Translates text between languages using deep-translator.
Preserves numerical values, coordinates, and units.

SAFETY: Translation is a pure linguistic operation.
It MUST NOT interpret marine safety data, alter recommendations,
paraphrase safety warnings to sound "nicer", or remove warnings.
Numbers, coordinates, and units MUST be preserved exactly.
"""

from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TranslationResult:
    """Result of text translation."""
    translated_text: str
    source_language: str
    target_language: str
    provider: str = "unknown"


class TranslationError(Exception):
    """Raised when translation fails."""
    pass


class TranslationProviderUnavailableError(TranslationError):
    """Raised when the translation provider is unreachable."""
    pass


class TranslationProvider(ABC):
    """Abstract interface for text translation."""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text from source to target language.

        Args:
            text: Text to translate.
            source_lang: ISO 639-1 source language code.
            target_lang: ISO 639-1 target language code.

        Returns:
            TranslationResult with translated text.

        Raises:
            TranslationError: On translation failure.
            TranslationProviderUnavailableError: When provider is unreachable.
        """

    # Languages verified to work with deep-translator's Google engine.
    VERIFIED_LANGUAGES = {"en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu"}


class GoogleTranslationProvider(TranslationProvider):
    """Translation using deep-translator's Google Translate engine.

    This is a free translation service. No API key required.
    Requires internet connectivity.
    """

    def __init__(self):
        try:
            from deep_translator import GoogleTranslator as _GT
            self._translator_class = _GT
        except ImportError:
            raise TranslationProviderUnavailableError(
                "deep-translator library not installed. "
                "Run: pip install deep-translator"
            )

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text using Google Translate."""
        if not text or not text.strip():
            return TranslationResult(
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                provider="google_translate"
            )

        # No translation needed for same language
        if source_lang == target_lang:
            return TranslationResult(
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                provider="google_translate"
            )

        try:
            # Protect numerical values, coordinates, and units from translation
            protected_text, placeholders = self._protect_values(text)

            translator = self._translator_class(source=source_lang, target=target_lang)
            translated = translator.translate(protected_text)

            # Restore protected values
            restored_text = self._restore_values(translated, placeholders)

            return TranslationResult(
                translated_text=restored_text,
                source_language=source_lang,
                target_language=target_lang,
                provider="google_translate"
            )
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise TranslationProviderUnavailableError(
                    f"Google Translate service unavailable: {e}"
                )
            raise TranslationError(f"Translation failed: {e}")

    @staticmethod
    def _protect_values(text: str) -> tuple[str, dict[str, str]]:
        """Replace numbers, coordinates, and units with placeholders.

        This prevents the translator from altering numerical data.
        """
        placeholders = {}
        counter = [0]

        def replace_match(match):
            key = f"__ORCA_NUM_{counter[0]}__"
            placeholders[key] = match.group(0)
            counter[0] += 1
            return key

        # Match: coordinates (9.9°N, 76.2°E), decimals, times, dates, units
        patterns = [
            r'\d+\.?\d*\s*°[NSEW]',        # Coordinates with direction
            r'\d+\.?\d*\s*(?:km|m|ft|nm|knots?|kt|mph|km/h|°C|°F|hPa|mb|mm)',  # Values with units
            r'\d{1,2}:\d{2}(?::\d{2})?',    # Times
            r'\d{4}-\d{2}-\d{2}',           # ISO dates
            r'-?\d+\.?\d*',                 # Plain numbers (last to avoid over-matching)
        ]

        protected = text
        for pattern in patterns:
            protected = re.sub(pattern, replace_match, protected)

        return protected, placeholders

    @staticmethod
    def _restore_values(text: str, placeholders: dict[str, str]) -> str:
        """Restore protected values in translated text."""
        restored = text
        for key, value in placeholders.items():
            restored = restored.replace(key, value)
        return restored


class TestTranslationProvider(TranslationProvider):
    """Deterministic translation provider for testing.

    Supports a small set of hard-coded translations for testing
    the voice pipeline without network access.
    """

    # Verified test translations (English <-> Hindi only for testing)
    _TEST_TRANSLATIONS = {
        ("hi", "en"): {
            "कोच्चि के पास सुरक्षित मछली पकड़ने की जगह खोजें": "Find safe fishing spot near Kochi",
            "कल सुबह मछली पकड़ना": "Fishing tomorrow morning",
        },
        ("en", "hi"): {
            "Safe fishing recommended near Kochi": "कोच्चि के पास सुरक्षित मछली पकड़ने की सिफारिश",
            "Unsafe conditions detected": "असुरक्षित स्थितियाँ पाई गईं",
            "Insufficient evidence for safety assessment": "सुरक्षा मूल्यांकन के लिए अपर्याप्त साक्ष्य",
        },
    }

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Return deterministic test translation."""
        if source_lang == target_lang:
            return TranslationResult(
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                provider="test"
            )

        key = (source_lang, target_lang)
        translations = self._TEST_TRANSLATIONS.get(key, {})
        translated = translations.get(text, f"[{target_lang}] {text}")

        return TranslationResult(
            translated_text=translated,
            source_language=source_lang,
            target_language=target_lang,
            provider="test"
        )


def get_translation_provider() -> TranslationProvider:
    """Factory: get the configured translation provider.

    Controlled by ORCA_TRANSLATION_PROVIDER env var:
      - "google" (default): Google Translate via deep-translator
      - "test": Deterministic test provider
    """
    provider_name = os.environ.get("ORCA_TRANSLATION_PROVIDER", "google")

    if provider_name == "test":
        return TestTranslationProvider()
    elif provider_name == "google":
        return GoogleTranslationProvider()
    else:
        raise TranslationError(f"Unknown translation provider: {provider_name}")
