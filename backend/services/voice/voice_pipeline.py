"""
M4 Voice Pipeline Orchestrator.

Coordinates the full voice flow:

    Audio
      ↓
    STT
      ↓
    Language Detection / Explicit Language
      ↓
    Translation
      ↓
    Intent Extraction
      ↓
    M4 Backend (M2 → M1)
      ↓
    Response Formatting
      ↓
    Translation
      ↓
    TTS

SAFETY INVARIANT:
This orchestrator is a TRANSPORT layer.

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
from dataclasses import dataclass
from typing import Optional

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse

from backend.services.voice.stt_provider import (
    STTProvider,
    STTProviderError,
    STTProviderUnavailableError,
    get_stt_provider,
)

from backend.services.voice.language_detector import (
    LanguageDetector,
    LanguageDetectionError,
    get_language_detector,
)

from backend.services.voice.translation_provider import (
    TranslationProvider,
    TranslationError,
    TranslationProviderUnavailableError,
    get_translation_provider,
)

from backend.services.voice.tts_provider import (
    TTSProvider,
    TTSProviderError,
    TTSProviderUnavailableError,
    TTSUnsupportedLanguageError,
    get_tts_provider,
)

from backend.services.voice.intent_extractor import (
    extract_intent,
    ClarificationRequired,
)

from backend.services.voice.response_formatter import (
    ResponseFormatter,
)


# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = {
    "en",
    "hi",
    "ta",
    "te",
    "ml",
    "kn",
    "bn",
    "mr",
    "gu",
}


LANGUAGE_ALIASES = {
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


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class VoicePipelineError(Exception):
    """Base error for voice pipeline failures."""


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

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
            result["translated_transcript"] = (
                self.translated_transcript
            )

        result["response_text"] = self.response_text

        if self.audio_base64:
            result["audio_base64"] = self.audio_base64
            result["audio_format"] = self.audio_format

        if self.decision:
            result["decision"] = self.decision

        if self.clarification_message:
            result["clarification_message"] = (
                self.clarification_message
            )

        if self.missing_fields:
            result["missing_fields"] = self.missing_fields

        return result


# ---------------------------------------------------------------------------
# Voice Pipeline
# ---------------------------------------------------------------------------

class VoicePipeline:
    """
    Orchestrates the complete M4 voice pipeline.

    The pipeline performs transport/orchestration only.

    Decision authority remains:

        M4 → M2 → M1

    Providers are injectable for deterministic testing.
    """

    def __init__(
        self,
        stt: Optional[STTProvider] = None,
        language_detector: Optional[LanguageDetector] = None,
        translator: Optional[TranslationProvider] = None,
        tts: Optional[TTSProvider] = None,
    ):
        self.stt = stt or get_stt_provider()
        self.language_detector = (
            language_detector or get_language_detector()
        )
        self.translator = (
            translator or get_translation_provider()
        )
        self.tts = tts or get_tts_provider()

    # =======================================================================
    # LANGUAGE HELPERS
    # =======================================================================

    @staticmethod
    def _normalize_language(
        language: Optional[str],
    ) -> str:
        """
        Normalize language names and locale codes.
        """

        if not language:
            return "en"

        normalized = language.strip().lower()

        return LANGUAGE_ALIASES.get(
            normalized,
            normalized,
        )

    def _resolve_language(
        self,
        text: str,
        explicit_language: Optional[str] = None,
    ) -> str:
        """
        Resolve input language.

        Priority:

            1. Explicit API language
            2. Automatic language detector
            3. English fallback
        """

        # ---------------------------------------------------------------
        # Explicit language supplied by API
        # ---------------------------------------------------------------

        if explicit_language:

            normalized = self._normalize_language(
                explicit_language
            )

            if normalized in SUPPORTED_LANGUAGES:
                return normalized

        # ---------------------------------------------------------------
        # Automatic detection
        # ---------------------------------------------------------------

        try:
            lang_result = self.language_detector.detect(
                text
            )

            detected_language = self._normalize_language(
                lang_result.language_code
            )

            if detected_language in SUPPORTED_LANGUAGES:
                return detected_language

        except LanguageDetectionError:
            pass

        except Exception:
            pass

        # ---------------------------------------------------------------
        # Safe fallback
        # ---------------------------------------------------------------

        return "en"

    # =======================================================================
    # AUDIO INPUT
    # =======================================================================

    def process_audio_bytes(
        self,
        audio_bytes: bytes,
        decision_handler,
        sample_rate: int = 16000,
    ) -> VoiceResponse:
        """
        Process raw WAV audio through the complete voice pipeline.

        Audio → STT → language → translation → intent → M4 backend.
        """

        if not audio_bytes:
            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language="unknown",
                transcript="",
                response_text=(
                    "No audio was provided. Please try again."
                ),
                clarification_message=(
                    "No audio was provided. Please try again."
                ),
            )

        # ---------------------------------------------------------------
        # Stage 1: STT
        # ---------------------------------------------------------------

        try:
            stt_result = self.stt.recognize(
                audio_bytes,
                sample_rate,
            )

        except STTProviderUnavailableError as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    "Speech recognition service is unavailable: "
                    f"{exc}"
                ),
            )

        except STTProviderError as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    f"Speech recognition failed: {exc}"
                ),
            )

        except Exception as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    f"Speech recognition failed: {exc}"
                ),
            )

        # ---------------------------------------------------------------
        # STT result
        # ---------------------------------------------------------------

        transcript = stt_result.text

        if not transcript or not transcript.strip():
            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language="unknown",
                transcript="",
                response_text=(
                    "No speech was recognized. Please try again."
                ),
                clarification_message=(
                    "No speech was recognized. Please try again."
                ),
            )

        # ---------------------------------------------------------------
        # Continue through text pipeline.
        #
        # STT result may optionally expose language information.
        # Existing providers that do not expose it remain compatible.
        # ---------------------------------------------------------------

        stt_language = getattr(
            stt_result,
            "language_code",
            None,
        )

        if stt_language is None:
            stt_language = getattr(
                stt_result,
                "language",
                None,
            )

        return self._process_from_text(
            transcript,
            decision_handler,
            explicit_language=stt_language,
        )

    # =======================================================================
    # AUDIO FILE
    # =======================================================================

    def process_audio_file(
        self,
        file_path: str,
        decision_handler,
    ) -> VoiceResponse:
        """
        Process a WAV audio file through the complete voice pipeline.
        """

        # ---------------------------------------------------------------
        # STT
        # ---------------------------------------------------------------

        try:
            stt_result = self.stt.recognize_file(
                file_path
            )

        except STTProviderUnavailableError as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    "Speech recognition service is unavailable: "
                    f"{exc}"
                ),
            )

        except STTProviderError as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    f"Speech recognition failed: {exc}"
                ),
            )

        except Exception as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language="unknown",
                transcript="",
                response_text=(
                    f"Speech recognition failed: {exc}"
                ),
            )

        transcript = stt_result.text

        if not transcript or not transcript.strip():
            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language="unknown",
                transcript="",
                response_text=(
                    "No speech was recognized. Please try again."
                ),
            )

        stt_language = getattr(
            stt_result,
            "language_code",
            None,
        )

        if stt_language is None:
            stt_language = getattr(
                stt_result,
                "language",
                None,
            )

        return self._process_from_text(
            transcript,
            decision_handler,
            explicit_language=stt_language,
        )

    # =======================================================================
    # TEXT INPUT
    # =======================================================================

    def process_text(
        self,
        text: str,
        decision_handler,
        language: Optional[str] = None,
    ) -> VoiceResponse:
        """
        Process text input through the complete voice pipeline.

        `language` is optional.

        If provided:
            the supported explicit language is used.

        If omitted:
            the existing automatic language detector is used.

        This keeps backward compatibility with existing callers:

            pipeline.process_text(text, handler)

        while also supporting:

            pipeline.process_text(
                text,
                handler,
                language="ml",
            )
        """

        return self._process_from_text(
            text,
            decision_handler,
            explicit_language=language,
        )

    # =======================================================================
    # CORE TEXT PIPELINE
    # =======================================================================

    def _process_from_text(
        self,
        text: str,
        decision_handler,
        explicit_language: Optional[str] = None,
    ) -> VoiceResponse:
        """
        Core pipeline:

            text
              ↓
            language
              ↓
            translation
              ↓
            intent
              ↓
            DecisionRequest
              ↓
            M4 backend
              ↓
            response formatting
              ↓
            translation
              ↓
            TTS
        """

        # ---------------------------------------------------------------
        # Validate input
        # ---------------------------------------------------------------

        if not text or not text.strip():
            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language="unknown",
                transcript="",
                response_text=(
                    "No speech was recognized. Please try again."
                ),
                clarification_message=(
                    "No speech was recognized. Please try again."
                ),
            )

        text = text.strip()

        # ---------------------------------------------------------------
        # Stage 2: Language
        # ---------------------------------------------------------------

        detected_language = self._resolve_language(
            text=text,
            explicit_language=explicit_language,
        )

        # ---------------------------------------------------------------
        # Stage 3: Translation → English
        # ---------------------------------------------------------------

        translated_text = text

        if detected_language != "en":

            try:
                translation_result = (
                    self.translator.translate(
                        text,
                        source_lang=detected_language,
                        target_lang="en",
                    )
                )

                translated_text = (
                    translation_result.translated_text
                )

            except (
                TranslationError,
                TranslationProviderUnavailableError,
            ) as exc:

                return VoiceResponse(
                    status="SERVICE_UNAVAILABLE",
                    language=detected_language,
                    transcript=text,
                    translated_transcript=None,
                    response_text=(
                        "Translation service is unavailable: "
                        f"{exc}"
                    ),
                )

            except Exception as exc:

                return VoiceResponse(
                    status="SERVICE_UNAVAILABLE",
                    language=detected_language,
                    transcript=text,
                    translated_transcript=None,
                    response_text=(
                        "Translation service is unavailable: "
                        f"{exc}"
                    ),
                )

            if not translated_text or not translated_text.strip():
                return VoiceResponse(
                    status="SERVICE_UNAVAILABLE",
                    language=detected_language,
                    transcript=text,
                    translated_transcript=None,
                    response_text=(
                        "The request could not be translated safely."
                    ),
                )

        # ---------------------------------------------------------------
        # Stage 4: Intent Extraction
        # ---------------------------------------------------------------

        try:
            intent_result = extract_intent(
                translated_text
            )

        except Exception as exc:
            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language=detected_language,
                transcript=text,
                translated_transcript=(
                    translated_text
                    if detected_language != "en"
                    else None
                ),
                response_text=(
                    f"Intent extraction failed: {exc}"
                ),
            )

        # ---------------------------------------------------------------
        # Clarification required
        # ---------------------------------------------------------------

        if isinstance(
            intent_result,
            ClarificationRequired,
        ):

            clarification_text = (
                intent_result.message
            )

            # -----------------------------------------------------------
            # Translate clarification back to user language
            # -----------------------------------------------------------

            if detected_language != "en":

                try:
                    tr = self.translator.translate(
                        clarification_text,
                        source_lang="en",
                        target_lang=detected_language,
                    )

                    clarification_text = (
                        tr.translated_text
                    )

                except (
                    TranslationError,
                    TranslationProviderUnavailableError,
                ):
                    # Safe fallback:
                    # preserve authoritative English clarification.
                    pass

            # -----------------------------------------------------------
            # TTS
            # -----------------------------------------------------------

            audio_b64, audio_fmt = (
                self._synthesize_safe(
                    clarification_text,
                    detected_language,
                )
            )

            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language=detected_language,
                transcript=text,
                translated_transcript=(
                    translated_text
                    if detected_language != "en"
                    else None
                ),
                response_text=clarification_text,
                audio_base64=audio_b64,
                audio_format=audio_fmt,
                clarification_message=(
                    intent_result.message
                ),
                missing_fields=list(
                    intent_result.missing_fields
                ),
            )

        # ---------------------------------------------------------------
        # Stage 5: Build DecisionRequest
        # ---------------------------------------------------------------

        try:
            decision_request = DecisionRequest(
                query=intent_result.query,
                location=intent_result.location,
                date=intent_result.date,
                time=intent_result.time,
                activity=intent_result.activity,
                vessel_type=intent_result.vessel_type,
            )

        except Exception as exc:

            return VoiceResponse(
                status="CLARIFICATION_REQUIRED",
                language=detected_language,
                transcript=text,
                translated_transcript=(
                    translated_text
                    if detected_language != "en"
                    else None
                ),
                response_text=(
                    "I need more information before I can "
                    f"make a safe recommendation: {exc}"
                ),
            )

        # ---------------------------------------------------------------
        # Stage 6: M4 Backend
        #
        # Voice does NOT make the decision.
        #
        # decision_handler:
        #
        #     M4 → M2 → M1
        # ---------------------------------------------------------------

        try:
            decision_response = decision_handler(
                decision_request
            )

        except Exception as exc:

            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language=detected_language,
                transcript=text,
                translated_transcript=(
                    translated_text
                    if detected_language != "en"
                    else None
                ),
                response_text=(
                    f"Decision service failed: {exc}"
                ),
            )

        # ---------------------------------------------------------------
        # Stage 7: Format authoritative decision
        # ---------------------------------------------------------------

        try:
            response_text_en = (
                ResponseFormatter.format_for_speech(
                    decision_response,
                    language="en",
                )
            )

        except Exception as exc:

            return VoiceResponse(
                status="SERVICE_UNAVAILABLE",
                language=detected_language,
                transcript=text,
                translated_transcript=(
                    translated_text
                    if detected_language != "en"
                    else None
                ),
                response_text=(
                    f"Response formatting failed: {exc}"
                ),
                decision=self._serialize_decision(
                    decision_response
                ),
            )

        # ---------------------------------------------------------------
        # Stage 8: Translate response to user's language
        # ---------------------------------------------------------------

        response_text_final = response_text_en

        if detected_language != "en":

            try:
                tr = self.translator.translate(
                    response_text_en,
                    source_lang="en",
                    target_lang=detected_language,
                )

                translated_response = (
                    tr.translated_text
                )

                if translated_response:
                    response_text_final = (
                        translated_response
                    )

            except (
                TranslationError,
                TranslationProviderUnavailableError,
            ):
                # Safe fallback:
                # retain authoritative English response.
                response_text_final = (
                    response_text_en
                )

            except Exception:
                response_text_final = (
                    response_text_en
                )

        # ---------------------------------------------------------------
        # Stage 9: TTS
        # ---------------------------------------------------------------

        audio_b64, audio_fmt = (
            self._synthesize_safe(
                response_text_final,
                detected_language,
            )
        )

        # ---------------------------------------------------------------
        # Final response
        # ---------------------------------------------------------------

        return VoiceResponse(
            status=(
                decision_response.status.value
                if hasattr(
                    decision_response.status,
                    "value",
                )
                else str(
                    decision_response.status
                )
            ),
            language=detected_language,
            transcript=text,
            translated_transcript=(
                translated_text
                if detected_language != "en"
                else None
            ),
            response_text=response_text_final,
            audio_base64=audio_b64,
            audio_format=audio_fmt,
            decision=self._serialize_decision(
                decision_response
            ),
        )

    # =======================================================================
    # TTS
    # =======================================================================

    def _synthesize_safe(
        self,
        text: str,
        language: str,
    ) -> tuple[
        Optional[str],
        Optional[str],
    ]:
        """
        Attempt TTS synthesis.

        TTS failure is NON-FATAL.

        TTS cannot modify the decision.

        If the requested language is unsupported by TTS,
        English is attempted as a presentation fallback.
        """

        if not text:
            return None, None

        # ---------------------------------------------------------------
        # Primary requested language
        # ---------------------------------------------------------------

        try:

            tts_result = self.tts.synthesize(
                text,
                language,
            )

            audio_b64 = base64.b64encode(
                tts_result.audio_bytes
            ).decode("utf-8")

            return (
                audio_b64,
                tts_result.audio_format,
            )

        except TTSUnsupportedLanguageError:

            # -----------------------------------------------------------
            # Safe English TTS fallback
            #
            # This does NOT alter the decision.
            # -----------------------------------------------------------

            try:

                tts_result = self.tts.synthesize(
                    text,
                    "en",
                )

                audio_b64 = base64.b64encode(
                    tts_result.audio_bytes
                ).decode("utf-8")

                return (
                    audio_b64,
                    tts_result.audio_format,
                )

            except (
                TTSProviderError,
                TTSProviderUnavailableError,
            ):
                return None, None

        except (
            TTSProviderError,
            TTSProviderUnavailableError,
        ):
            return None, None

        except Exception:
            return None, None

    # =======================================================================
    # SERIALIZATION
    # =======================================================================

    @staticmethod
    def _serialize_decision(
        decision,
    ) -> Optional[dict]:

        if decision is None:
            return None

        if isinstance(
            decision,
            dict,
        ):
            return decision

        if hasattr(
            decision,
            "model_dump",
        ):
            return decision.model_dump()

        if hasattr(
            decision,
            "dict",
        ):
            return decision.dict()

        if hasattr(
            decision,
            "__dict__",
        ):
            return dict(
                decision.__dict__
            )

        return {
            "value": str(decision)
        }


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "VoicePipeline",
    "VoicePipelineError",
    "VoiceResponse",
    "SUPPORTED_LANGUAGES",
]