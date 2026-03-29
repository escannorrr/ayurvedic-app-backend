import os
from dotenv import load_dotenv
load_dotenv()

from app.services.ai_pipeline import run_pipeline
import json

def test_enhanced_confidence():
    query = "I have a sharp burning sensation in my stomach, especially after eating spicy food. I also feel very irritable and hot."
    print(f"Testing Diagnosis for query: {query}")
    
    result = run_pipeline(query)
    
    print("\n--- Diagnostic Results ---")
    print(f"Overall Confidence: {result.get('confidence')}%")
    
    for item in result.get("diagnosis", []):
        print(f"Condition: {item['condition']}")
        print(f"Confidence: {item['confidence']}%")
        print(f"Label: {item['label']}")
        print("-" * 20)

if __name__ == "__main__":
    test_enhanced_confidence()
