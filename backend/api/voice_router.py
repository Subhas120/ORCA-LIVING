"""
M4 Voice API Router.

Provides the POST /api/v1/voice endpoint for the voice pipeline.

Accepts audio files or text input. Returns structured decision
responses with optional TTS audio output.

SAFETY:
    This router delegates all decisions to the existing M4
    backend (M2 → M1).

    It MUST NOT independently assess marine safety.
    It MUST NOT override M1 recommendations.
    It MUST NOT override M2 safety evaluations.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.m1_service import M1Service
from backend.services.m2_adapter import (
    InsufficientEvidenceError,
    M2Adapter,
    M2AdapterError,
)
from backend.services.response_adapter import ResponseAdapter
from backend.services.voice.voice_pipeline import VoicePipeline


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class VoiceTextRequest(BaseModel):
    """
    Request model for JSON text-based voice input.

    This endpoint skips STT but still performs:
        language → translation → intent → M2 → M1 → response → TTS
    """

    text: str
    language: Optional[str] = None


class VoiceAPIResponse(BaseModel):
    """
    Public response model for the voice endpoint.
    """

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


# ---------------------------------------------------------------------------
# Shared M4 backend instances
# ---------------------------------------------------------------------------

m1_service = M1Service()
m2_adapter = M2Adapter()


# ---------------------------------------------------------------------------
# Decision orchestration
# ---------------------------------------------------------------------------

def _run_decision(
    decision_request: DecisionRequest,
) -> DecisionResponse:
    """
    Execute the authoritative M4 decision pipeline.

    Architecture:

        Voice
          ↓
        M4 Router
          ↓
        M2 Marine State + Safety
          ↓
        M1 Decision Intelligence
          ↓
        M4 Response Adapter
          ↓
        Voice

    IMPORTANT:
        This function does not make marine decisions itself.
    """

    # =======================================================================
    # Stage 1: M2 marine state + safety
    # =======================================================================

    try:
        world_state, proposals, safety_evals = (
            m2_adapter.get_marine_state_and_safety(
                decision_request
            )
        )

    except InsufficientEvidenceError as exc:
        return DecisionResponse(
            status=StatusEnum.INSUFFICIENT_EVIDENCE,
            decisionSummary=str(exc),
        )

    except M2AdapterError as exc:
        return DecisionResponse(
            status=StatusEnum.SERVICE_UNAVAILABLE,
            decisionSummary=str(exc),
        )

    # =======================================================================
    # Stage 2: M1 Decision Intelligence
    # =======================================================================

    try:
        decision_intel = (
            m1_service.run_decision_pipeline(
                world_state,
                proposals,
                safety_evals,
                decision_request,
            )
        )

    except Exception as exc:
        # Fail closed.
        #
        # Do NOT fabricate a recommendation when M1 fails.
        return DecisionResponse(
            status=StatusEnum.SERVICE_UNAVAILABLE,
            decisionSummary=(
                f"M1 pipeline failed: {exc}"
            ),
        )

    # =======================================================================
    # Stage 3: Determine public status
    # =======================================================================

    if not decision_intel.recommended_candidate_id:
        status = StatusEnum.NO_SAFE_CANDIDATES
    else:
        status = StatusEnum.DECISION_AVAILABLE

    # =======================================================================
    # Stage 4: M1 → M4 response adaptation
    # =======================================================================

    # The adapter receives the original M2 proposals so it can resolve
    # candidate IDs and preserve candidate classifications.
    return ResponseAdapter.adapt(
        decision_intel,
        status,
        proposals,
    )


# ---------------------------------------------------------------------------
# POST /voice
# ---------------------------------------------------------------------------

@router.post(
    "/voice",
    response_model=VoiceAPIResponse,
)
async def voice_endpoint(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
):
    """
    Main voice endpoint.

    Accepts either:

        1. audio file
        2. text form field

    Optional:
        language

    Audio flow:

        Audio
          ↓
        STT
          ↓
        Language
          ↓
        Translation
          ↓
        Intent
          ↓
        M4/M2/M1
          ↓
        Response
          ↓
        Translation
          ↓
        TTS

    Text flow:

        Text
          ↓
        Explicit language / detection
          ↓
        Translation
          ↓
        Intent
          ↓
        M4/M2/M1
          ↓
        Response
          ↓
        Translation
          ↓
        TTS
    """

    try:
        pipeline = VoicePipeline()

        # ===================================================================
        # Audio input
        # ===================================================================

        if audio is not None:

            audio_bytes = await audio.read()

            if not audio_bytes:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded audio file is empty",
                )

            result = pipeline.process_audio_bytes(
                audio_bytes,
                _run_decision,
            )

        # ===================================================================
        # Text input
        # ===================================================================

        elif text is not None:

            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Text input cannot be empty",
                )

            result = pipeline.process_text(
                text=text,
                decision_handler=_run_decision,
                language=language,
            )

        # ===================================================================
        # No input
        # ===================================================================

        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Either 'audio' file or 'text' field "
                    "is required"
                ),
            )

        # ===================================================================
        # Response
        # ===================================================================

        return VoiceAPIResponse(
            **result.to_dict()
        )

    except HTTPException:
        raise

    except Exception as exc:
        # Voice orchestration failure.
        #
        # Do not manufacture a decision.
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {exc}",
        )


# ---------------------------------------------------------------------------
# POST /voice/text
# ---------------------------------------------------------------------------

@router.post(
    "/voice/text",
    response_model=VoiceAPIResponse,
)
async def voice_text_endpoint(
    request: VoiceTextRequest,
):
    """
    Text-only voice endpoint.

    Accepts JSON:

        {
            "text": "...",
            "language": "ml"
        }

    The explicit language is passed into VoicePipeline.

    Example Malayalam request:

        {
            "text":
                "കൊച്ചിയിൽ നാളെ രാവിലെ സുരക്ഷിതമായ മത്സ്യബന്ധന സ്ഥലം കണ്ടെത്തുക",
            "language": "ml"
        }

    Flow:

        Malayalam
          ↓
        VoicePipeline
          ↓
        English translation
          ↓
        Intent extraction
          ↓
        DecisionRequest
          ↓
        M4
          ↓
        M2
          ↓
        M1
          ↓
        M4 response
          ↓
        Malayalam translation
          ↓
        TTS
    """

    try:

        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text input cannot be empty",
            )

        pipeline = VoicePipeline()

        result = pipeline.process_text(
            text=request.text,
            decision_handler=_run_decision,
            language=request.language,
        )

        return VoiceAPIResponse(
            **result.to_dict()
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {exc}",
        )