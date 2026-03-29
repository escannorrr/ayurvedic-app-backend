from app.utils.formatting import normalize_symptoms

def test_normalization_consistency():
    # Case 1: Order and Punctuation
    q1 = "Fever and weakness"
    q2 = "weakness, fever"
    assert normalize_symptoms(q1) == normalize_symptoms(q2)
    print(f"✅ Match: '{q1}' == '{q2}' -> '{normalize_symptoms(q1)}'")

    # Case 2: Duplicates and Case
    q3 = "Headache, Headache, fever"
    q4 = "FEVER, headache"
    assert normalize_symptoms(q3) == normalize_symptoms(q4)
    print(f"✅ Match: '{q3}' == '{q4}' -> '{normalize_symptoms(q3)}'")

    # Case 3: Stop words
    q5 = "pain in the joints"
    q6 = "joints pain"
    assert normalize_symptoms(q5) == normalize_symptoms(q6)
    print(f"✅ Match: '{q5}' == '{q6}' -> '{normalize_symptoms(q5)}'")

if __name__ == "__main__":
    test_normalization_consistency()
    print("🚀 Consistency tests passed!")
