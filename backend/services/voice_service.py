"""M4 Voice Service Stub."""

class VoiceService:
    @staticmethod
    def recognize_speech(audio_file) -> str:
        """Stub for STT."""
        return "Find a safe fishing spot."
        
    @staticmethod
    def detect_language(text: str) -> str:
        """Stub for language detection."""
        return "en"
        
    @staticmethod
    def translate(text: str, target_lang: str) -> str:
        """Stub for translation."""
        return text
        
    @staticmethod
    def text_to_speech(text: str, lang: str):
        """Stub for TTS."""
        pass
