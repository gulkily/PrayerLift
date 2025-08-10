import requests
import os
from typing import Optional
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

class TTSService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        # Using Rachel voice (ID for expressive, warm voice)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Generate audio from text using ElevenLabs API"""
        
        if not self.api_key:
            return None
            
        if not voice_id:
            voice_id = self.default_voice_id
            
        url = f"{self.base_url}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"TTS generation error: {e}")
            return None
    
    def generate_audio_base64(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """Generate audio and return as base64 string for web playback"""
        audio_bytes = self.generate_audio(text, voice_id)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('utf-8')
        return None
    
    def get_available_voices(self) -> list:
        """Get list of available voices from ElevenLabs"""
        if not self.api_key:
            return []
            
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                voices_data = response.json()
                return voices_data.get("voices", [])
        except Exception as e:
            print(f"Error fetching voices: {e}")
            
        return []

# Global service instance
tts_service = TTSService()