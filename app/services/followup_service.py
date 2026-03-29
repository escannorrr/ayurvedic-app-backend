import logging
import os
from typing import List, Dict, Any
from groq import Groq

logger = logging.getLogger(__name__)

class FollowupService:
    """
    Generates clinically useful follow-up questions to refine Ayurvedic assessments
    when initial symptoms are vague or incomplete.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

    def generate_followup(self, query: str, history_context: str, dosha_scores: Dict[str, float] = None) -> str:
        """
        Analyzes the current interaction and identifies missing clinical data 
        (Ashta Vidha Pariksha) to ask targeted questions.
        """
        if not self.api_key:
            return "Could you tell me more about your digestion and daily routine?"

        try:
            client = Groq(api_key=self.api_key)
            
            dosha_text = f"Primary Dosha Tendency: {max(dosha_scores, key=dosha_scores.get) if dosha_scores else 'General'}"
            
            system_prompt = """You are a senior Ayurvedic clinical expert. Your task is to identify MISSING clinical information from a patient's symptoms.
            
            Ayurvedic diagnostic pillars (Ashta Vidha Pariksha):
            - Nadi (Pulse)
            - Mutra (Urine)
            - Mala (Stool)
            - Jihva (Tongue)
            - Shabda (Voice)
            - Sparsha (Touch/Temperature)
            - Drig (Eyes)
            - Akriti (Physique)
            
            Common clinical gaps: 
            - Agni (Digestion/Appetite)
            - Nidra (Sleep quality)
            - Koshtha (Bowel movement)
            - Bala (Energy levels)
            
            Instruction:
            - Based on the user symptoms and history, ask EXACTLY 1 or 2 targeted, short, and clinically useful questions.
            - Focus on identifying the root Dosha imbalance.
            - Avoid repeating questions already answered in the history.
            - Be empathetic but professional.
            
            Example output: 'How is your appetite? Do you feel a heavy sensation after eating?'
            """
            
            user_msg = f"User Symptoms: {query}\n{dosha_text}\nSession Context:\n{history_context}"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.4,
                max_tokens=100
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return "Could you provide more details about how you are feeling overall?"

# Singleton instance
followup_service = FollowupService()
