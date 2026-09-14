# backend/services/voice/translation_provider.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import re
from typing import Optional


class TranslationError(Exception):
    """Base translation error."""


class TranslationProviderUnavailableError(TranslationError):
    """Raised when the translation service is unavailable."""


@dataclass(frozen=True)
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    provider: str

    @property
    def translated_text(self) -> str:
        return self.text


class TranslationProvider(ABC):
    """Interface for translation providers used by M4."""

    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> TranslationResult:
        raise NotImplementedError


def _normalize_language(
    value: Optional[str],
    default: str,
) -> str:
    if not value:
        return default

    value = value.strip().lower()

    aliases = {
        "english": "en",
        "en-us": "en",
        "en-gb": "en",
        "hindi": "hi",
        "tamil": "ta",
        "telugu": "te",
        "malayalam": "ml",
        "kannada": "kn",
        "bengali": "bn",
        "marathi": "mr",
        "gujarati": "gu",
    }

    return aliases.get(value, value)


def _protect_identifiers(
    text: str,
) -> tuple[str, dict[str, str]]:
    """
    Protect numbers, coordinates, and distances from translation.
    """

    protected: dict[str, str] = {}

    pattern = re.compile(
        r"""
        \b\d+(?:\.\d+)?\s*°?\s*[NSEW]\b
        |
        \b\d+(?:\.\d+)?\s*(?:km|m|nm)\b
        |
        \b\d+(?:\.\d+)?\b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    counter = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal counter

        token = f"ORCA_NUM_{counter}_TOKEN"
        protected[token] = match.group(0)
        counter += 1

        return token

    return pattern.sub(replace, text), protected


def _restore_identifiers(
    text: str,
    protected: dict[str, str],
) -> str:
    for token, original in protected.items():
        text = text.replace(token, original)

    return text


class GoogleTranslationProvider(TranslationProvider):
    """
    Real translation provider.

    GoogleTranslator is attempted first.
    MyMemoryTranslator is used as fallback.
    """

    def translate(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> TranslationResult:

        source = _normalize_language(
            source_lang or source_language,
            "auto",
        )

        target = _normalize_language(
            target_lang or target_language,
            "en",
        )

        clean_text = text.strip() if text else ""

        if not clean_text:
            return TranslationResult(
                text="",
                source_language=source,
                target_language=target,
                provider="google",
            )

        # Translation is unnecessary when both languages are identical.
        if source != "auto" and source == target:
            return TranslationResult(
                text=clean_text,
                source_language=source,
                target_language=target,
                provider="passthrough",
            )

        protected_text, protected = _protect_identifiers(
            clean_text
        )

        google_error: Optional[Exception] = None

        try:
            from deep_translator import GoogleTranslator

            translated = GoogleTranslator(
                source=source,
                target=target,
            ).translate(protected_text)

            if translated:
                return TranslationResult(
                    text=_restore_identifiers(
                        translated,
                        protected,
                    ),
                    source_language=source,
                    target_language=target,
                    provider="google",
                )

        except Exception as exc:
            google_error = exc

        try:
            from deep_translator import MyMemoryTranslator

            translated = MyMemoryTranslator(
                source="auto" if source == "auto" else source,
                target=target,
            ).translate(protected_text)

            if translated:
                return TranslationResult(
                    text=_restore_identifiers(
                        translated,
                        protected,
                    ),
                    source_language=source,
                    target_language=target,
                    provider="mymemory",
                )

        except Exception as fallback_error:
            raise TranslationProviderUnavailableError(
                "Both Google and MyMemory translation providers "
                "are unavailable."
            ) from (
                fallback_error
                if google_error is None
                else google_error
            )

        raise TranslationProviderUnavailableError(
            "Translation provider returned no translation."
        )


class TestTranslationProvider(TranslationProvider):
    """
    Deterministic provider used by the M4 automated test suite.

    Contract:
      - same language -> exact passthrough
      - known fixture -> deterministic translation
      - unknown text -> [target] text
    """

    TRANSLATIONS = {
        (
            "कल सुबह मछली पकड़ना",
            "hi",
            "en",
        ): "Fishing tomorrow morning",

        (
            "कोच्चि के पास कल सुबह मछली पकड़ने के लिए एक अच्छी जगह खोजें",
            "hi",
            "en",
        ): "Find a good place to fish tomorrow morning near Kochi",

        (
            "कोच्चि के पास मछली पकड़ने के लिए एक अच्छी जगह खोजें",
            "hi",
            "en",
        ): "Find a good fishing spot near Kochi",

        (
            "find a good place to fish tomorrow morning near kochi",
            "en",
            "hi",
        ): "कोच्चि के पास कल सुबह मछली पकड़ने के लिए एक अच्छी जगह खोजें",
    }

    def translate(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> TranslationResult:

        source = _normalize_language(
            source_lang or source_language,
            "en",
        )

        target = _normalize_language(
            target_lang or target_language,
            "en",
        )

        clean_text = text.strip() if text else ""

        # TEST CONTRACT:
        # "hello", "en", "en" -> "hello"
        if source == target:
            return TranslationResult(
                text=clean_text,
                source_language=source,
                target_language=target,
                provider="test",
            )

        key = (
            clean_text,
            source,
            target,
        )

        translated = self.TRANSLATIONS.get(key)

        if translated is None:
            key = (
                clean_text.lower(),
                source,
                target,
            )

            translated = self.TRANSLATIONS.get(key)

        # TEST CONTRACT:
        # unknown text must be prefixed with [target].
        if translated is None:
            translated = f"[{target}] {clean_text}"

        return TranslationResult(
            text=translated,
            source_language=source,
            target_language=target,
            provider="test",
        )


def get_translation_provider(
    provider: Optional[str] = None,
) -> TranslationProvider:

    selected = (
        provider
        or os.getenv("ORCA_TRANSLATION_PROVIDER")
        or "google"
    ).strip().lower()

    if selected in {
        "test",
        "mock",
        "offline",
    }:
        return TestTranslationProvider()

    if selected in {
        "google",
        "mymemory",
        "auto",
    }:
        return GoogleTranslationProvider()

    raise ValueError(
        f"Unsupported translation provider: {selected}"
    )


__all__ = [
    "TranslationError",
    "TranslationProviderUnavailableError",
    "TranslationResult",
    "TranslationProvider",
    "GoogleTranslationProvider",
    "TestTranslationProvider",
    "get_translation_provider",
]