from app.utils.formatting import format_as_percentage, format_string_percentages

def test_decimal_conversion():
    assert format_as_percentage(0.2587) == "25.87%"
    assert format_as_percentage(0.67) == "67%"
    assert format_as_percentage(0.1) == "10%"
    assert format_as_percentage(0.0) == "0%"
    assert format_as_percentage(1.0) == "100%"
    assert format_as_percentage(0.9999) == "99.99%"

def test_no_conversion_above_one():
    assert format_as_percentage(1.1) == "1.1" # Standard float representation
    assert format_as_percentage(77) == "77"
    assert format_as_percentage(2024) == "2024"

def test_string_replacement():
    text = "The match score of 0.2587 for Jwara. Dosha pitta is 0.67."
    expected = "The match score of 25.87% for Jwara. Dosha pitta is 67%."
    assert format_string_percentages(text) == expected

def test_mixed_strings():
    text = "Case #1024. Date: 2024-03-27. Score: 0.85"
    expected = "Case #1024. Date: 2024-03-27. Score: 85%"
    assert format_string_percentages(text) == expected

if __name__ == "__main__":
    test_decimal_conversion()
    test_no_conversion_above_one()
    test_string_replacement()
    test_mixed_strings()
    print("✅ All formatting unit tests passed!")
