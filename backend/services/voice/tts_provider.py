"""M4 Text-to-Speech provider abstraction.

Provides TTS via gTTS (Google Text-to-Speech) and pyttsx3 (offline).
Provider selection is controlled by the ORCA_TTS_PROVIDER env var.

Available providers:
  - "gtts":    Google Text-to-Speech (requires internet, multilingual)
  - "pyttsx3": Offline TTS via OS speech engine (limited languages)
  - "test":    Deterministic test provider (returns empty bytes)

SAFETY: TTS is a pure audio synthesis layer. It MUST NOT alter,
paraphrase, or omit safety-critical content from the text.
All warnings, unsafe statuses, and uncertainty information
MUST be spoken exactly as provided.
"""

from __future__ import annotations

import io
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TTSResult:
    """Result of text-to-speech synthesis."""
    audio_bytes: bytes
    audio_format: str  # e.g. "mp3", "wav"
    language: str
    provider: str = "unknown"


class TTSProviderError(Exception):
    """Raised when TTS synthesis fails."""
    pass


class TTSProviderUnavailableError(TTSProviderError):
    """Raised when the TTS provider is unreachable."""
    pass


class TTSUnsupportedLanguageError(TTSProviderError):
    """Raised when the requested language is not supported."""
    pass


class TTSProvider(ABC):
    """Abstract interface for text-to-speech providers."""

    @abstractmethod
    def synthesize(self, text: str, language: str) -> TTSResult:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize.
            language: ISO 639-1 language code.

        Returns:
            TTSResult with audio bytes.

        Raises:
            TTSProviderError: On synthesis failure.
            TTSProviderUnavailableError: When provider is unreachable.
            TTSUnsupportedLanguageError: When language is not supported.
        """

    @abstractmethod
    def supported_languages(self) -> set[str]:
        """Return set of supported language codes."""


class GTTSProvider(TTSProvider):
    """TTS using Google Text-to-Speech (gTTS).

    Free, requires internet. Supports many languages including
    Indian languages (hi, ta, te, ml, kn, bn, mr, gu).

    Output format: MP3
    """

    SUPPORTED = {
        "en", "hi", "ta", "te", "ml", "kn", "bn", "mr", "gu", "pa",
        "fr", "de", "es", "pt", "it", "nl", "ru", "zh-CN", "ja", "ko",
        "ar", "th", "vi", "id", "ms", "tl", "ur",
    }

    def __init__(self):
        try:
            from gtts import gTTS as _gTTS
            self._gTTS = _gTTS
        except ImportError:
            raise TTSProviderUnavailableError(
                "gTTS library not installed. Run: pip install gTTS"
            )

    def synthesize(self, text: str, language: str) -> TTSResult:
        """Synthesize speech using gTTS."""
        if not text or not text.strip():
            raise TTSProviderError("Cannot synthesize empty text")

        if language not in self.SUPPORTED:
            raise TTSUnsupportedLanguageError(
                f"Language '{language}' is not supported by gTTS. "
                f"Supported: {sorted(self.SUPPORTED)}"
            )

        try:
            tts = self._gTTS(text=text, lang=language, slow=False)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            audio_bytes = buffer.getvalue()

            return TTSResult(
                audio_bytes=audio_bytes,
                audio_format="mp3",
                language=language,
                provider="gtts"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "connection" in error_str or "timeout" in error_str or "network" in error_str:
                raise TTSProviderUnavailableError(
                    f"gTTS service unavailable: {e}"
                )
            raise TTSProviderError(f"TTS synthesis failed: {e}")

    def supported_languages(self) -> set[str]:
        return self.SUPPORTED.copy()


class Pyttsx3Provider(TTSProvider):
    """Offline TTS using pyttsx3 (OS speech engine).

    Works without internet. Language support depends on
    the installed OS speech voices.

    Output format: WAV (saved to temp file, read back)
    """

    def __init__(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
        except ImportError:
            raise TTSProviderUnavailableError(
                "pyttsx3 library not installed. Run: pip install pyttsx3"
            )
        except Exception as e:
            raise TTSProviderUnavailableError(
                f"pyttsx3 initialization failed: {e}"
            )

    def synthesize(self, text: str, language: str) -> TTSResult:
        """Synthesize speech using pyttsx3."""
        if not text or not text.strip():
            raise TTSProviderError("Cannot synthesize empty text")

        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            self._engine.save_to_file(text, tmp_path)
            self._engine.runAndWait()

            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            os.unlink(tmp_path)

            return TTSResult(
                audio_bytes=audio_bytes,
                audio_format="wav",
                language=language,
                provider="pyttsx3"
            )
        except Exception as e:
            raise TTSProviderError(f"pyttsx3 synthesis failed: {e}")

    def supported_languages(self) -> set[str]:
        # pyttsx3 language support depends on OS voices
        return {"en"}


class TestTTSProvider(TTSProvider):
    """Deterministic TTS provider for testing.

    Returns minimal valid audio-like bytes for testing the pipeline
    without actual speech synthesis.
    """

    SUPPORTED = {"en", "hi", "ta", "te", "ml"}

    def synthesize(self, text: str, language: str) -> TTSResult:
        """Return deterministic test audio bytes."""
        if not text or not text.strip():
            raise TTSProviderError("Cannot synthesize empty text")

        if language not in self.SUPPORTED:
            raise TTSUnsupportedLanguageError(
                f"Test TTS does not support language '{language}'"
            )

        # Return minimal bytes that identify the text+language for test assertion
        marker = f"TTS:{language}:{text}".encode("utf-8")
        return TTSResult(
            audio_bytes=marker,
            audio_format="test",
            language=language,
            provider="test"
        )

    def supported_languages(self) -> set[str]:
        return self.SUPPORTED.copy()


def get_tts_provider() -> TTSProvider:
    """Factory: get the configured TTS provider.

    Controlled by ORCA_TTS_PROVIDER env var:
      - "gtts" (default): Google Text-to-Speech
      - "pyttsx3": Offline OS TTS
      - "test": Deterministic test provider
    """
    provider_name = os.environ.get("ORCA_TTS_PROVIDER", "gtts")

    if provider_name == "test":
        return TestTTSProvider()
    elif provider_name == "gtts":
        return GTTSProvider()
    elif provider_name == "pyttsx3":
        return Pyttsx3Provider()
    else:
        raise TTSProviderError(f"Unknown TTS provider: {provider_name}")
