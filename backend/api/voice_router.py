"""M4 Voice API router.

Voice is a transport/interface layer. It owns no marine reasoning.

The voice pipeline performs speech/language handling and delegates the
actual decision request to the same DecisionService used by REST. This
ensures identical M2 safety, M1 decision semantics and M4 response fields
for text and voice interfaces.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.models.request import DecisionRequest
from backend.services.decision_service import decision_service
from backend.services.voice.voice_pipeline import VoicePipeline


router = APIRouter()


class VoiceTextRequest(BaseModel):
    """JSON request for text input through the voice/language pipeline."""

    text: str
    language: Optional[str] = None


class VoiceAPIResponse(BaseModel):
    """Public response model for voice requests."""

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


def _run_decision(decision_request: DecisionRequest):
    """Delegate to the single authoritative M4 decision service.

    No decision logic is duplicated here. REST and voice therefore share:
        M2 -> M1 -> M4 response adaptation
    """
    return decision_service.run(decision_request)


@router.post(
    "/voice",
    response_model=VoiceAPIResponse,
)
async def voice_endpoint(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
):
    """Process audio or text through the M4 voice pipeline."""
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

        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'audio' file or 'text' field is required",
            )

        return VoiceAPIResponse(**result.to_dict())

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {exc}",
        ) from exc


@router.post(
    "/voice/text",
    response_model=VoiceAPIResponse,
)
async def voice_text_endpoint(
    request: VoiceTextRequest,
):
    """Process JSON text through the same voice and decision pipeline."""
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

        return VoiceAPIResponse(**result.to_dict())

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice pipeline error: {exc}",
        ) from exc
