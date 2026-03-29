import os
import sys
import logging
import json
from dotenv import load_dotenv

load_dotenv()

# Set up logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ensure the root directory is in the PYTHONPATH so we can import services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_pipeline import run_pipeline

def test_query(query):
    print(f"\n{'='*50}")
    print(f"--- Running RAG Pipeline Test ---")
    print(f"User Query: '{query}'")
    print(f"{'='*50}\n")
    
    # Returns a Python Dictionary now instead of raw string
    response = run_pipeline(query)
    
    print(f"\n{'='*50}")
    print(f"--- Final Structured JSON Response ---")
    print(f"{'='*50}\n")
    print(json.dumps(response, indent=2))
    print(f"\n{'='*50}")

def main():
    queries = [
        "I have fever, headache and body pain",
        "I have acidity and burning sensation",
        "Joint pain and stiffness",
        "Loss of appetite and weakness"
    ]
    for q in queries:
        test_query(q)

if __name__ == "__main__":
    main()
