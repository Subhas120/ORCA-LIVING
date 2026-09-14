"""M4 Speech-to-Text provider abstraction.

Defines a clean STTProvider interface and implementations.
Provider selection is controlled by the ORCA_STT_PROVIDER env var.

Available providers:
  - "google_web": Google Web Speech API (free, requires internet)
  - "test":       Deterministic test provider (offline, for testing)

SAFETY: STT is a pure transcription layer. It MUST NOT interpret,
filter, or alter the meaning of recognized speech.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Optional


@dataclass(frozen=True)
class STTResult:
    """Result of speech-to-text recognition."""
    text: str
    confidence: Optional[float] = None
    provider: str = "unknown"


class STTProviderError(Exception):
    """Raised when the STT provider fails."""
    pass


class STTProviderUnavailableError(STTProviderError):
    """Raised when the STT provider cannot be reached."""
    pass


class STTProvider(ABC):
    """Abstract interface for speech-to-text providers."""

    @abstractmethod
    def recognize(self, audio_data: bytes, sample_rate: int = 16000) -> STTResult:
        """Recognize speech from raw audio bytes.

        Args:
            audio_data: Raw audio bytes (WAV format expected).
            sample_rate: Sample rate of the audio in Hz.

        Returns:
            STTResult with recognized text.

        Raises:
            STTProviderError: On recognition failure.
            STTProviderUnavailableError: When provider is unreachable.
        """

    @abstractmethod
    def recognize_file(self, file_path: str) -> STTResult:
        """Recognize speech from an audio file.

        Args:
            file_path: Path to a WAV audio file.

        Returns:
            STTResult with recognized text.

        Raises:
            STTProviderError: On recognition failure.
            STTProviderUnavailableError: When provider is unreachable.
        """


class GoogleWebSTTProvider(STTProvider):
    """STT using Google Web Speech API via SpeechRecognition library.

    This uses the free Google Web Speech API. It requires internet
    connectivity and has no guaranteed uptime or SLA.

    No API key is required for the free tier.
    For production, set GOOGLE_APPLICATION_CREDENTIALS for Google Cloud
    Speech-to-Text instead.
    """

    def __init__(self):
        try:
            import speech_recognition as sr
            self._sr = sr
            self._recognizer = sr.Recognizer()
        except ImportError:
            raise STTProviderUnavailableError(
                "SpeechRecognition library not installed. "
                "Run: pip install SpeechRecognition"
            )

    def recognize(self, audio_data: bytes, sample_rate: int = 16000) -> STTResult:
        """Recognize speech from raw audio bytes."""
        try:
            audio = self._sr.AudioData(audio_data, sample_rate, 2)
            text = self._recognizer.recognize_google(audio)
            return STTResult(text=text, confidence=None, provider="google_web")
        except self._sr.UnknownValueError:
            raise STTProviderError("Google Web STT could not understand the audio")
        except self._sr.RequestError as e:
            raise STTProviderUnavailableError(
                f"Google Web STT service unavailable: {e}"
            )

    def recognize_file(self, file_path: str) -> STTResult:
        """Recognize speech from a WAV file."""
        try:
            with self._sr.AudioFile(file_path) as source:
                audio = self._recognizer.record(source)
            text = self._recognizer.recognize_google(audio)
            return STTResult(text=text, confidence=None, provider="google_web")
        except self._sr.UnknownValueError:
            raise STTProviderError("Google Web STT could not understand the audio")
        except self._sr.RequestError as e:
            raise STTProviderUnavailableError(
                f"Google Web STT service unavailable: {e}"
            )
        except FileNotFoundError:
            raise STTProviderError(f"Audio file not found: {file_path}")
        except Exception as e:
            raise STTProviderError(f"STT failed: {e}")


class TestSTTProvider(STTProvider):
    """Deterministic STT provider for testing.

    Returns pre-configured responses for testing the voice pipeline
    without requiring actual audio processing or network access.

    Set test phrases via constructor or use the default.
    """

    def __init__(self, default_text: str = "Find safe fishing near Kochi tomorrow morning"):
        self._default_text = default_text
        self._file_responses: dict[str, str] = {}

    def set_response(self, file_path: str, text: str):
        """Pre-configure a response for a specific file path."""
        self._file_responses[file_path] = text

    def recognize(self, audio_data: bytes, sample_rate: int = 16000) -> STTResult:
        """Return deterministic test text."""
        return STTResult(
            text=self._default_text,
            confidence=1.0,
            provider="test"
        )

    def recognize_file(self, file_path: str) -> STTResult:
        """Return pre-configured or default text."""
        text = self._file_responses.get(file_path, self._default_text)
        return STTResult(
            text=text,
            confidence=1.0,
            provider="test"
        )


def get_stt_provider() -> STTProvider:
    """Factory: get the configured STT provider.

    Controlled by ORCA_STT_PROVIDER env var:
      - "google_web" (default): Google Web Speech API
      - "test": Deterministic test provider

    Returns:
        An STTProvider instance.
    """
    provider_name = os.environ.get("ORCA_STT_PROVIDER", "google_web")

    if provider_name == "test":
        return TestSTTProvider()
    elif provider_name == "google_web":
        return GoogleWebSTTProvider()
    else:
        raise STTProviderError(f"Unknown STT provider: {provider_name}")
