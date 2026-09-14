"""M4 Voice Pipeline Orchestrator.

Coordinates the full voice flow:
  Audio → STT → Language Detection → Translation → Intent Extraction
  → M4 Backend (M2 → M1) → Response Formatting → Translation → TTS

SAFETY INVARIANT: This orchestrator is a TRANSPORT layer.
It MUST NOT:
  - perform marine safety reasoning
  - override M1/M2 safety decisions
  - convert unsafe → safe
  - fabricate data
  - guess decision-critical fields
  - remove or paraphrase safety warnings
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Optional

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.voice.stt_provider import (
    STTProvider, STTResult, STTProviderError, STTProviderUnavailableError,
    get_stt_provider,
)
from backend.services.voice.language_detector import (
    LanguageDetector, LanguageDetectionResult, LanguageDetectionError,
    get_language_detector,
)
from backend.services.voice.translation_provider import (
    TranslationProvider, TranslationResult, TranslationError,
    TranslationProviderUnavailableError, get_translation_provider,
)
from backend.services.voice.tts_provider import (
    TTSProvider, TTSResult, TTSProviderError, TTSProviderUnavailableError,
    TTSUnsupportedLanguageError, get_tts_provider,
)
from backend.services.voice.intent_extractor import (
    extract_intent, ExtractedIntent, ClarificationRequired,
)
from backend.services.voice.response_formatter import ResponseFormatter


class VoicePipelineError(Exception):
    """Base error for voice pipeline failures."""
    pass


@dataclass
class VoiceResponse:
    """Complete voice pipeline response."""
    status: str
    language: str
    transcript: str
    translated_transcript: Optional[str] = None
    response_text: str = ""
    audio_base64: Optional[str] = None
    audio_format: Optional[str] = None
    decision: Optional[dict] = None
    clarification_message: Optional[str] = None
    missing_fields: Optional[list[str]] = None

    def to_dict(self) -> dict:
        result = {
            "status": self.status,
            "language": self.language,
            "transcript": self.transcript,
        }
        if self.translated_transcript:
            result["translated_transcript"] = self.translated_transcript
        result["response_text"] = self.response_text
        if self.audio_base64:
            result["audio_base64"] = self.audio_base64
            result["audio_format"] = self.audio_format
        if self.decision:
            result["decision"] = self.decision
        if self.clarification_message:
            result["clarification_message"] = self.clarification_message
        if self.missing_fields:
            result["missing_fields"] = self.missing_fields
        return result


class VoicePipeline:
    """Orchestrates the complete M4 voice pipeline.

    This class wires together STT, language detection, translation,
    intent extraction, backend decision, response formatting,
    response translation, and TTS.

    All providers are injectable for testing.
    """

    def __init__(
        self,
        stt: Optional[STTProvider] = None,
        language_detector: Optional[LanguageDetector] = None,
        translator: Optional[TranslationProvider] = None,
        tts: Optional[TTSProvider] = None,
    ):
        self.stt = stt or get_stt_provider()
        self.language_detector = language_detector or get_language_detector()
        self.translator = translator or get_translation_provider()
        self.tts = tts or get_tts_provider()

    def process_audio_bytes(
        self,
        audio_bytes: bytes,
        decision_handler,
        sample_rate: int = 16000,
    ) -> VoiceResponse:
        """Process raw audio bytes through the full voice pipeline.

        Args:
            audio_bytes: Raw audio data (WAV format).
            decision_handler: Callable that takes a DecisionRequest
                and returns a DecisionResponse. This is the M4 backend.
            sample_rate: Audio sample rate in Hz.

        Returns:
            VoiceResponse with the complete pipeline result.
        """
        # Stage 1: Speech-to-Text
        try:
            stt_result = self.stt.recognize(audio_bytes, sample_rate)
        except STTProviderUnavailableError as e:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=f"Speech recognition service is unavailable: {e}",
            )
        except STTProviderError as e:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=f"Speech recognition failed: {e}",
            )

        return self._process_from_text(stt_result.text, decision_handler)

    def process_audio_file(
        self,
        file_path: str,
        decision_handler,
    ) -> VoiceResponse:
        """Process an audio file through the full voice pipeline.

        Args:
            file_path: Path to a WAV audio file.
            decision_handler: Callable that takes a DecisionRequest
                and returns a DecisionResponse.

        Returns:
            VoiceResponse with the complete pipeline result.
        """
        # Stage 1: Speech-to-Text
        try:
            stt_result = self.stt.recognize_file(file_path)
        except STTProviderUnavailableError as e:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=f"Speech recognition service is unavailable: {e}",
            )
        except STTProviderError as e:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=f"Speech recognition failed: {e}",
            )

        return self._process_from_text(stt_result.text, decision_handler)

    def process_text(
        self,
        text: str,
        decision_handler,
    ) -> VoiceResponse:
        """Process text directly (skipping STT) through the voice pipeline.

        Useful for testing or text-based input with voice output.

        Args:
            text: Input text in any supported language.
            decision_handler: Callable that takes a DecisionRequest
                and returns a DecisionResponse.

        Returns:
            VoiceResponse with the complete pipeline result.
        """
        return self._process_from_text(text, decision_handler)

    def _process_from_text(
        self,
        text: str,
        decision_handler,
    ) -> VoiceResponse:
        """Core pipeline: text → language → translate → intent → decision → response → TTS.

        Args:
            text: Recognized text from STT.
            decision_handler: The M4 backend decision function.

        Returns:
            VoiceResponse with the full pipeline result.
        """
        if not text or not text.strip():
            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language="unknown",
                transcript="",
                response_text="No speech was recognized. Please try again.",
                clarification_message="No speech was recognized. Please try again.",
            )

        # Stage 2: Language Detection
        try:
            lang_result = self.language_detector.detect(text)
            detected_language = lang_result.language_code
        except LanguageDetectionError:
            # Default to English if detection fails
            detected_language = "en"

        # Stage 3: Translation to English (for intent extraction and M4 backend)
        translated_text = text
        if detected_language != "en":
            try:
                translation_result = self.translator.translate(
                    text, source_lang=detected_language, target_lang="en"
                )
                translated_text = translation_result.translated_text
            except (TranslationError, TranslationProviderUnavailableError) as e:
                return VoiceResponse(
                    status="SERVICE_UNAVAILABLE",
                    language=detected_language,
                    transcript=text,
                    response_text=f"Translation service is unavailable: {e}",
                )

        # Stage 4: Intent Extraction
        intent_result = extract_intent(translated_text)

        if isinstance(intent_result, ClarificationRequired):
            # Translate clarification message back to user's language
            clarification_text = intent_result.message
            if detected_language != "en":
                try:
                    tr = self.translator.translate(
                        clarification_text, source_lang="en", target_lang=detected_language
                    )
                    clarification_text = tr.translated_text
                except (TranslationError, TranslationProviderUnavailableError):
                    pass  # Keep English clarification

            # Generate TTS for clarification
            audio_b64, audio_fmt = self._synthesize_safe(clarification_text, detected_language)

            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language=detected_language,
                transcript=text,
                translated_transcript=translated_text if detected_language != "en" else None,
                response_text=clarification_text,
                audio_base64=audio_b64,
                audio_format=audio_fmt,
                clarification_message=intent_result.message,
                missing_fields=list(intent_result.missing_fields),
            )

        # Stage 5: Call M4 Backend (which calls M2 → M1)
        decision_request = DecisionRequest(
            query=intent_result.query,
            location=intent_result.location,
            date=intent_result.date,
            time=intent_result.time,
            activity=intent_result.activity,
            vessel_type=intent_result.vessel_type,
        )

        try:
            decision_response = decision_handler(decision_request)
        except Exception as e:
            error_text = f"Decision service failed: {e}"
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language=detected_language,
                transcript=text,
                translated_transcript=translated_text if detected_language != "en" else None,
                response_text=error_text,
            )

        # Stage 6: Format response for speech
        response_text_en = ResponseFormatter.format_for_speech(
            decision_response, language="en"
        )

        # Stage 7: Translate response to user's language
        response_text_final = response_text_en
        if detected_language != "en":
            try:
                tr = self.translator.translate(
                    response_text_en, source_lang="en", target_lang=detected_language
                )
                response_text_final = tr.translated_text
            except (TranslationError, TranslationProviderUnavailableError):
                response_text_final = response_text_en  # Fallback to English

        # Stage 8: Text-to-Speech
        audio_b64, audio_fmt = self._synthesize_safe(response_text_final, detected_language)

        return VoiceResponse(
            status=decision_response.status.value,
            language=detected_language,
            transcript=text,
            translated_transcript=translated_text if detected_language != "en" else None,
            response_text=response_text_final,
            audio_base64=audio_b64,
            audio_format=audio_fmt,
            decision=decision_response.model_dump(),
        )

    def _synthesize_safe(self, text: str, language: str) -> tuple[Optional[str], Optional[str]]:
        """Attempt TTS synthesis, returning None on failure.

        TTS failure is non-fatal — the text response is still returned.
        """
        try:
            tts_result = self.tts.synthesize(text, language)
            audio_b64 = base64.b64encode(tts_result.audio_bytes).decode("utf-8")
            return audio_b64, tts_result.audio_format
        except TTSUnsupportedLanguageError:
            # Try English fallback
            try:
                tts_result = self.tts.synthesize(text, "en")
                audio_b64 = base64.b64encode(tts_result.audio_bytes).decode("utf-8")
                return audio_b64, tts_result.audio_format
            except TTSProviderError:
                return None, None
        except (TTSProviderError, TTSProviderUnavailableError):
            return None, None
