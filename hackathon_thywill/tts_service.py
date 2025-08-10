import requests
import os
import hashlib
from typing import Optional
from dotenv import load_dotenv
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

class TTSService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        # Using voices optimized for spiritual content
        self.default_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Sarah - warm, gentle, reverent
        # Alternative: "21m00Tcm4TlvDq8ikWAM"  # Rachel - expressive
        # Alternative: "AZnzlk1XvdvUeBnXmlld"  # Domi - calm, soothing
        
        # Setup audio cache directory
        self.cache_dir = Path("audio_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, text: str, voice_id: str) -> str:
        """Generate cache key from text and voice ID"""
        content = f"{text}_{voice_id}_eleven_multilingual_v2"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Retrieve cached audio if exists"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        if cache_file.exists():
            try:
                return cache_file.read_bytes()
            except Exception:
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes) -> None:
        """Save audio data to cache"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        try:
            cache_file.write_bytes(audio_data)
        except Exception as e:
            print(f"Failed to cache audio: {e}")
    
    def _format_prayer_text(self, text: str) -> str:
        """Format prayer text for more reverent and expressive delivery"""
        
        # Add pauses and emphasis for spiritual content
        formatted = text
        
        # Add slight pauses after sacred names and titles
        sacred_words = [
            ("God", "God,"), ("Lord", "Lord,"), ("Jesus", "Jesus,"), 
            ("Christ", "Christ,"), ("Father", "Father,"), ("Holy Spirit", "Holy Spirit,"),
            ("Divine", "Divine,"), ("Creator", "Creator,"), ("Almighty", "Almighty,")
        ]
        
        for original, replacement in sacred_words:
            # Only replace if not already followed by punctuation
            import re
            pattern = rf'\b{re.escape(original)}\b(?![,.:;!?])'
            formatted = re.sub(pattern, replacement, formatted)
        
        # Add pauses after prayer transitions
        transitions = [
            ("We pray", "We pray,"),
            ("May you", "May you,"), 
            ("May they", "May they,"),
            ("Grant", "Grant,"),
            ("Bless", "Bless,"),
            ("Guide", "Guide,")
        ]
        
        for original, replacement in transitions:
            formatted = formatted.replace(original, replacement)
        
        # Add reverent pause before Amen
        formatted = formatted.replace(" Amen.", "... Amen.")
        formatted = formatted.replace(" Amen", "... Amen")
        formatted = formatted.replace(".Amen", "... Amen")
        
        # Emphasize key spiritual concepts with slight pauses
        emphasis_words = ["peace", "strength", "healing", "wisdom", "love", "grace", "mercy"]
        for word in emphasis_words:
            # Add slight pause before important spiritual words
            formatted = formatted.replace(f" {word}", f" {word}")
        
        return formatted
        
    def generate_audio(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Generate audio from text using ElevenLabs API with caching"""
        
        if not self.api_key:
            return None
            
        if not voice_id:
            voice_id = self.default_voice_id
        
        # Check cache first
        cache_key = self._get_cache_key(text, voice_id)
        cached_audio = self._get_cached_audio(cache_key)
        if cached_audio:
            return cached_audio
            
        url = f"{self.base_url}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Pre-process text for more reverent delivery
        formatted_text = self._format_prayer_text(text)
        
        data = {
            "text": formatted_text,
            "model_id": "eleven_multilingual_v2",  # Better model for expressiveness
            "voice_settings": {
                "stability": 0.2,        # Even lower for more emotional variation
                "similarity_boost": 0.9, # Higher for voice consistency
                "style": 0.8,            # Maximum expressiveness
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Save to cache before returning
                audio_data = response.content
                self._save_to_cache(cache_key, audio_data)
                return audio_data
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