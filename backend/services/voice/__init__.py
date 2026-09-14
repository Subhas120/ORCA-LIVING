"""M4 Voice subsystem.

Provides speech-to-text, language detection, translation,
intent extraction, and text-to-speech for the ORCA-LIVING
multilingual voice pipeline.

SAFETY INVARIANT: Voice is a TRANSPORT layer only.
It MUST NOT perform marine safety reasoning, invent thresholds,
override M1/M2 safety decisions, or fabricate scientific data.
"""
