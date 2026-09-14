"""M4 Voice API Router.

Provides the POST /api/v1/voice endpoint for the voice pipeline.

Accepts audio files or text input. Returns structured decision
responses with optional TTS audio output.

SAFETY: This router delegates all decisions to the existing M4
backend (M2 → M1). It MUST NOT independently assess marine safety.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.m2_adapter import (
    M2Adapter,
    M2AdapterError,
    InsufficientEvidenceError,
)
from backend.services.m1_service import M1Service
from backend.services.response_adapter import ResponseAdapter
from backend.services.voice.voice_pipeline import VoicePipeline


router = APIRouter()


class VoiceTextRequest(BaseModel):
    """Request model for text-based voice input (skips STT)."""

    text: str
    language: Optional[str] = None


class VoiceAPIResponse(BaseModel):
    """Response model for the voice endpoint."""

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


# Shared M4 backend instances
m1_service = M1Service()
m2_adapter = M2Adapter()


def _run_decision(request: DecisionRequest) -> DecisionResponse:
    """Execute the M4 decision pipeline (M2 → M1).

    This is the same pipeline used by the /api/v1/decision endpoint.
    The voice layer calls this instead of duplicating the logic.
    """

    # ---------------------------------------------------------
    # Stage 1: M2 marine state + safety
    # ---------------------------------------------------------
    try:
        world_state, proposals, safety_evals = (
            m2_adapter.get_marine_state_and_safety(request)
        )

    except InsufficientEvidenceError as e:
        return DecisionResponse(
            status=StatusEnum.INSUFFICIENT_EVIDENCE,
            decisionSummary=str(e),
        )

    except M2AdapterError as e:
        return DecisionResponse(
            status=StatusEnum.SERVICE_UNAVAILABLE,
            decisionSummary=str(e),
        )

    # ---------------------------------------------------------
    # Stage 2: M1 decision intelligence
    # ---------------------------------------------------------
    try:
        decision_intel = m1_service.run_decision_pipeline(
            world_state,
            proposals,
            safety_evals,
            request,
        )

    except Exception as e:
        return DecisionResponse(
            status=StatusEnum.SERVICE_UNAVAILABLE,
            decisionSummary=f"M1 pipeline failed: {e}",
        )

    # ---------------------------------------------------------
    # Stage 3: Determine public status
    # ---------------------------------------------------------
    if not decision_intel.recommended_candidate_id:
        status = StatusEnum.NO_SAFE_CANDIDATES
    else:
        status = StatusEnum.DECISION_AVAILABLE

    # IMPORTANT:
    # Pass the M2 proposals into the response adapter.
    # The adapter needs them to resolve the recommended
    # candidate ID into the complete public Candidate object.
    return ResponseAdapter.adapt(
        decision_intel,
        status,
        proposals,
    )


@router.post("/voice", response_model=VoiceAPIResponse)
async def voice_endpoint(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    """Voice endpoint: audio or text → decision → spoken response.

    Accepts either:
      - An audio file upload (WAV format)
      - A text string (for text-based input with voice output)

    Returns a VoiceAPIResponse with the decision, response text,
    and optional base64-encoded audio.
    """

    try:
        pipeline = VoicePipeline()

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

        elif text is not None:
            result = pipeline.process_text(
                text,
                _run_decision,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'audio' file or 'text' field is required",
            )

        return VoiceAPIResponse(**result.to_dict())

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {e}",
        )


@router.post("/voice/text", response_model=VoiceAPIResponse)
async def voice_text_endpoint(request: VoiceTextRequest):
    """Text-only voice endpoint.

    Accepts JSON with a text field and returns voice pipeline results.
    """

    try:
        pipeline = VoicePipeline()

        result = pipeline.process_text(
            request.text,
            _run_decision,
        )

        return VoiceAPIResponse(**result.to_dict())

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {e}",
        )