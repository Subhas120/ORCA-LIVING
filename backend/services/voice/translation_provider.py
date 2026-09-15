# backend/services/voice/translation_provider.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import re
from typing import Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TranslationError(Exception):
    """Base translation error."""


class TranslationProviderUnavailableError(TranslationError):
    """Raised when the translation service is unavailable."""


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    provider: str

    @property
    def translated_text(self) -> str:
        return self.text


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Language normalization
# ---------------------------------------------------------------------------

def _normalize_language(
    value: Optional[str],
    default: str,
) -> str:
    """
    Normalize language names / locale codes to the language codes
    used by the translation providers.
    """

    if not value:
        return default

    value = value.strip().lower()

    aliases = {
        "english": "en",
        "en-us": "en",
        "en-gb": "en",

        "hindi": "hi",
        "hi-in": "hi",

        "tamil": "ta",
        "ta-in": "ta",

        "telugu": "te",
        "te-in": "te",

        "malayalam": "ml",
        "ml-in": "ml",

        "kannada": "kn",
        "kn-in": "kn",

        "bengali": "bn",
        "bn-in": "bn",

        "marathi": "mr",
        "mr-in": "mr",

        "gujarati": "gu",
        "gu-in": "gu",
    }

    return aliases.get(value, value)


# ---------------------------------------------------------------------------
# Unicode handling
# ---------------------------------------------------------------------------

def _normalize_unicode(text: str) -> str:
    """
    Normalize Unicode without converting the text to ASCII.

    IMPORTANT:
    Malayalam / Hindi / Tamil / Telugu / Kannada and other Indic scripts
    must remain real Unicode strings throughout the M4 pipeline.

    We intentionally do NOT perform:
        encode("ascii", ...)
        decode("latin-1")
        encode("latin-1")
        replace(...)

    because those operations can create mojibake such as:
        à´...
    """

    if not text:
        return ""

    import unicodedata

    return unicodedata.normalize("NFC", text)


def _repair_common_mojibake(text: str) -> str:
    """
    Attempt to repair common UTF-8-as-Latin-1/Windows-1252 mojibake.

    This is intentionally conservative.

    Correct Unicode Malayalam should pass through unchanged.

    Example of broken text:
        à´•àµŠà´šàµ à´šà´¿

    If the text is already valid Unicode, no transformation is attempted.
    """

    if not text:
        return ""

    # These characters are strong indicators of UTF-8 mojibake.
    mojibake_markers = (
        "Ã",
        "Â",
        "â",
        "ð",
        "à",
        "¤",
        " ",
    )

    if not any(marker in text for marker in mojibake_markers):
        return text

    try:
        repaired = text.encode("latin-1").decode("utf-8")

        # Only accept the repair if it actually changes the text.
        # Otherwise keep the original.
        if repaired and repaired != text:
            return _normalize_unicode(repaired)

    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return text


def _prepare_text(text: str) -> str:
    """
    Normalize incoming text while preserving Unicode.

    The order is:
        1. strip whitespace
        2. normalize Unicode
        3. conservatively repair mojibake
        4. normalize again
    """

    if not text:
        return ""

    clean_text = text.strip()

    clean_text = _normalize_unicode(clean_text)

    clean_text = _repair_common_mojibake(clean_text)

    clean_text = _normalize_unicode(clean_text)

    return clean_text


# ---------------------------------------------------------------------------
# Protect numeric / scientific identifiers
# ---------------------------------------------------------------------------

def _protect_identifiers(
    text: str,
) -> tuple[str, dict[str, str]]:
    """
    Protect numbers, coordinates, and distances from translation.

    Examples:
        9.78
        76.12
        9.78 N
        76.12 E
        15 km
        2.5 m
        1.5 nm
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
    """
    Restore protected scientific identifiers after translation.
    """

    for token, original in protected.items():
        text = text.replace(token, original)

    return text


# ---------------------------------------------------------------------------
# Real provider
# ---------------------------------------------------------------------------

class GoogleTranslationProvider(TranslationProvider):
    """
    Real translation provider.

    Provider order:
        1. GoogleTranslator
        2. MyMemoryTranslator

    This class is used for actual runtime translation.

    It does not fabricate translations when providers fail.
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

        clean_text = _prepare_text(text)

        if not clean_text:
            return TranslationResult(
                text="",
                source_language=source,
                target_language=target,
                provider="google",
            )

        # No translation needed.
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

        # -------------------------------------------------------------------
        # Google
        # -------------------------------------------------------------------

        try:
            from deep_translator import GoogleTranslator

            translated = GoogleTranslator(
                source=source,
                target=target,
            ).translate(protected_text)

            if translated:
                translated = _prepare_text(translated)

                translated = _restore_identifiers(
                    translated,
                    protected,
                )

                return TranslationResult(
                    text=translated,
                    source_language=source,
                    target_language=target,
                    provider="google",
                )

        except Exception as exc:
            google_error = exc

        # -------------------------------------------------------------------
        # MyMemory fallback
        # -------------------------------------------------------------------

        try:
            from deep_translator import MyMemoryTranslator

            translated = MyMemoryTranslator(
                source="auto" if source == "auto" else source,
                target=target,
            ).translate(protected_text)

            if translated:
                translated = _prepare_text(translated)

                translated = _restore_identifiers(
                    translated,
                    protected,
                )

                return TranslationResult(
                    text=translated,
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


# ---------------------------------------------------------------------------
# Deterministic test provider
# ---------------------------------------------------------------------------

class TestTranslationProvider(TranslationProvider):
    """
    Deterministic provider used by the M4 automated test suite.

    Contract:
        - same language -> exact passthrough
        - known fixture -> deterministic translation
        - unknown text -> [target] text

    This provider is NOT intended to replace the production translation
    service.

    It exists so the complete M4 voice pipeline can be tested offline
    and reproducibly.
    """

    TRANSLATIONS = {

        # ================================================================
        # Hindi -> English
        # ================================================================

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

        # ================================================================
        # English -> Hindi
        # ================================================================

        (
            "find a good place to fish tomorrow morning near kochi",
            "en",
            "hi",
        ): "कोच्चि के पास कल सुबह मछली पकड़ने के लिए एक अच्छी जगह खोजें",

        # ================================================================
        # Malayalam -> English
        # ================================================================

        (
            "കൊച്ചിയിൽ നാളെ രാവിലെ സുരക്ഷിതമായ മത്സ്യബന്ധന സ്ഥലം കണ്ടെത്തുക",
            "ml",
            "en",
        ): "Find a safe fishing location in Kochi tomorrow morning",

        (
            "കൊച്ചിക്ക് സമീപം നാളെ രാവിലെ മത്സ്യബന്ധനത്തിന് നല്ല സ്ഥലം കണ്ടെത്തുക",
            "ml",
            "en",
        ): "Find a good fishing spot near Kochi tomorrow morning",

        (
            "കൊച്ചിക്ക് സമീപം മത്സ്യബന്ധനത്തിന് നല്ല സ്ഥലം കണ്ടെത്തുക",
            "ml",
            "en",
        ): "Find a good fishing spot near Kochi",

        (
            "കൊച്ചിയിൽ സുരക്ഷിതമായ മത്സ്യബന്ധന സ്ഥലം കണ്ടെത്തുക",
            "ml",
            "en",
        ): "Find a safe fishing location in Kochi",

        # ================================================================
        # English -> Malayalam
        # ================================================================

        (
            "find a safe fishing location in kochi tomorrow morning",
            "en",
            "ml",
        ): "കൊച്ചിയിൽ നാളെ രാവിലെ സുരക്ഷിതമായ മത്സ്യബന്ധന സ്ഥലം കണ്ടെത്തുക",

        (
            "find a good fishing spot near kochi tomorrow morning",
            "en",
            "ml",
        ): "കൊച്ചിക്ക് സമീപം നാളെ രാവിലെ മത്സ്യബന്ധനത്തിന് നല്ല സ്ഥലം കണ്ടെത്തുക",

        (
            "find a good fishing spot near kochi",
            "en",
            "ml",
        ): "കൊച്ചിക്ക് സമീപം മത്സ്യബന്ധനത്തിന് നല്ല സ്ഥലം കണ്ടെത്തുക",

        (
            "find a safe fishing location in kochi",
            "en",
            "ml",
        ): "കൊച്ചിയിൽ സുരക്ഷിതമായ മത്സ്യബന്ധന സ്ഥലം കണ്ടെത്തുക",
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

        clean_text = _prepare_text(text)

        # ---------------------------------------------------------------
        # Same language = exact Unicode-preserving passthrough
        # ---------------------------------------------------------------

        if source == target:
            return TranslationResult(
                text=clean_text,
                source_language=source,
                target_language=target,
                provider="test",
            )

        # ---------------------------------------------------------------
        # Exact fixture lookup
        # ---------------------------------------------------------------

        key = (
            clean_text,
            source,
            target,
        )

        translated = self.TRANSLATIONS.get(key)

        # ---------------------------------------------------------------
        # Case-insensitive lookup for Latin-script inputs
        # ---------------------------------------------------------------

        if translated is None:
            key = (
                clean_text.lower(),
                source,
                target,
            )

            translated = self.TRANSLATIONS.get(key)

        # ---------------------------------------------------------------
        # Deterministic fallback
        #
        # IMPORTANT:
        # This is a test-provider fallback only.
        # It must never be mistaken for a real translation.
        # ---------------------------------------------------------------

        if translated is None:
            translated = f"[{target}] {clean_text}"

        translated = _prepare_text(translated)

        return TranslationResult(
            text=translated,
            source_language=source,
            target_language=target,
            provider="test",
        )


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "TranslationError",
    "TranslationProviderUnavailableError",
    "TranslationResult",
    "TranslationProvider",
    "GoogleTranslationProvider",
    "TestTranslationProvider",
    "get_translation_provider",
]