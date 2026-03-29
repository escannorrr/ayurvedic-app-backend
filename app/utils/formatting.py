import re
from typing import Any

def format_as_percentage(value: Any) -> str:
    """
    Converts a decimal float (0.0 to 1.0) into a percentage string (e.g., "25.87%").
    If the value is already > 1, returns it as a string without modification.
    """
    try:
        val = float(value)
        if val <= 1.0:
            # Rounding to 2 decimal places as requested
            return f"{round(val * 100, 2):g}%"
        return f"{val:g}"
    except (ValueError, TypeError):
        return str(value)

def format_string_percentages(text: str) -> str:
    """
    Finds decimal patterns (e.g., 0.2587) in a string and converts them 
    to human-readable percentages (e.g., 25.87%).
    
    Regex matches decimals like 0.123, 0.5, but avoids leading/trailing 
    unrelated digits (like years 2024 or counts).
    """
    if not isinstance(text, str):
        return text

    # Pattern: Matches decimal numbers between 0.0 and 1.0
    # Specifically looking for: 0\.\d+
    # We use a negative lookbehind/lookahead to avoid matching mid-number decimals 
    # if they are part of a larger non-percentage number (though 0.x is usually a score).
    pattern = r"\b0\.\d+\b"
    
    def replacer(match):
        val_str = match.group(0)
        return format_as_percentage(val_str)

    return re.sub(pattern, replacer, text)

def normalize_symptoms(text: str) -> str:
    """
    Standardizes symptom input for consistent vector/keyword matching.
    - Lowercase
    - Remove punctuation
    - Sort tokens alphabetically
    - Remove duplicates
    
    Example: "Fever and weakness" -> "fever weakness"
    """
    if not text:
        return ""
    
    # 1. Lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 2. Tokenize and remove common stop words (optional but recommended)
    tokens = text.split()
    stop_words = {'and', 'the', 'is', 'a', 'an', 'of', 'with', 'for', 'in'}
    tokens = [t for t in tokens if t not in stop_words]
    
    # 3. Sort and deduplicate
    unique_sorted_tokens = sorted(list(set(tokens)))
    
    return " ".join(unique_sorted_tokens)
