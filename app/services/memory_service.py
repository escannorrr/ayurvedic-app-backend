import logging
import os
from typing import List, Dict, Any
from groq import Groq
from app.services.session_service import get_history

logger = logging.getLogger(__name__)

# Constants for token efficiency
MAX_RECENT_MESSAGES = 5
SUMMARY_THRESHOLD = 8

class MemoryService:
    """
    Maintains clinical relevance and token efficiency by managing 
    conversation history and summarization.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

    def get_conversational_context(self, session_id: str) -> str:
        """
        Retrieves recent history and builds a concise string context for the LLM.
        Summarizes if history exceeds the threshold.
        """
        if not session_id:
            return ""

        all_history = get_history(session_id, limit=20)
        if not all_history:
            return ""

        # If history is long, summarize the older parts
        if len(all_history) > SUMMARY_THRESHOLD:
            logger.info(f"History for session {session_id} is long. Generating summary...")
            summary = self._summarize_history(all_history[:-MAX_RECENT_MESSAGES])
            recent_turns = all_history[-MAX_RECENT_MESSAGES:]
            return f"Previously discussed summary: {summary}\n\nRecent turns:\n" + self._format_history(recent_turns)
        
        return self._format_history(all_history)

    def _format_history(self, messages: List[Dict[str, str]]) -> str:
        """Formats a list of messages into a readable context string."""
        return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])

    def _summarize_history(self, messages: List[Dict[str, str]]) -> str:
        """
        Uses LLM to condense long conversation history into a clinical summary 
        focusing on symptoms and dosha observations.
        """
        if not self.api_key:
            return "History too long to display."

        try:
            client = Groq(api_key=self.api_key)
            history_text = self._format_history(messages)
            
            system_prompt = """Summarize the following Ayurvedic clinical conversation history into a 2-line summary. 
            Focus ONLY on symptoms mentioned, suspected doshas, and previous advice given. Keep it professional."""
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": history_text}
                ],
                temperature=0.3,
                max_tokens=150
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Previously discussed clinical symptoms."

# Singleton instance for the service
memory_service = MemoryService()
