import requests
import json
import os
from typing import Optional

class ClaudeAIService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    def generate_prayer_response(self, prayer_request: str, author_name: str = "someone") -> Optional[str]:
        """Generate a compassionate AI prayer response to a prayer request"""
        
        if not self.api_key:
            return self._fallback_prayer()
            
        prompt = f"""You are a compassionate spiritual guide helping to craft prayer responses. 

Someone named {author_name} has shared this prayer request:
"{prayer_request}"

Please write a gentle, faith-affirming prayer response that:
- Acknowledges their specific situation with empathy
- Offers comfort and hope
- Uses inclusive, non-denominational spiritual language
- Ends with "Amen" or similar closing
- Keeps it concise (2-3 sentences)
- Focuses on peace, strength, healing, or guidance as appropriate

Write only the prayer response, nothing else."""

        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("content") and len(result["content"]) > 0:
                    return result["content"][0].get("text", "").strip()
                    
        except Exception as e:
            print(f"Claude API error: {e}")
            
        return self._fallback_prayer()
    
    def _fallback_prayer(self) -> str:
        """Fallback prayer when API is unavailable"""
        return "May you find peace and strength in this time. Know that you are held in love and that hope remains, even in difficult moments. Amen."

# Global service instance
ai_service = ClaudeAIService()