from main import extract_keyword, create_response

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def test(func):
    result = func()
    if result is False:
        print(f"\u274C {func.__name__}")  # red X

@test
def extract_keyword_basic_lowercase():
    """Test basic extraction with lowercase trigger"""
    result = extract_keyword("/u/xeqtbot dividend")
    return result == "dividend"

@test
def extract_keyword_basic_uppercase():
    """Test basic extraction with uppercase trigger"""
    result = extract_keyword("/U/XEQTBOT DIVIDEND")
    return result == "dividend"

@test
def extract_keyword_mixed_case():
    """Test extraction with mixed case trigger and keyword"""
    result = extract_keyword("/u/XeQtBoT DiViDeNd")
    return result == "dividend"

@test
def extract_keyword_without_leading_slash():
    """Test extraction without leading slash"""
    result = extract_keyword("u/xeqtbot lumpsum")
    return result == "lumpsum"

@test
def extract_keyword_with_text_before():
    """Test extraction when trigger appears in middle of message"""
    result = extract_keyword("Hey there /u/xeqtbot dca please help")
    return result == "dca"

@test
def extract_keyword_with_text_after():
    """Test extraction with text after keyword"""
    result = extract_keyword("/u/xeqtbot dividend thanks in advance")
    return result == "dividend"

@test
def extract_keyword_with_text_before_and_after():
    """Test extraction with text both before and after"""
    result = extract_keyword("Hello /u/xeqtbot lumpsum can you help?")
    return result == "lumpsum"

@test
def extract_keyword_multiple_spaces():
    """Test extraction with multiple spaces between trigger and keyword"""
    result = extract_keyword("/u/xeqtbot    dividend")
    return result == "dividend"

@test
def extract_keyword_no_keyword():
    """Test extraction when no keyword is provided"""
    result = extract_keyword("/u/xeqtbot")
    return result is None

@test
def extract_keyword_no_keyword_with_space():
    """Test extraction when only space after trigger"""
    result = extract_keyword("/u/xeqtbot ")
    return result is None

@test
def extract_keyword_wrong_username():
    """Test extraction with wrong username"""
    result = extract_keyword("/u/wrongbot dividend")
    return result is None

@test
def extract_keyword_partial_username():
    """Test extraction with partial username match"""
    result = extract_keyword("/u/xeqt dividend")
    return result is None

@test
def extract_keyword_no_space_after_username():
    """Test extraction without space after username"""
    result = extract_keyword("/u/xeqtbotdividend")
    return result is None

@test
def extract_keyword_empty_message():
    """Test extraction with empty message"""
    result = extract_keyword("")
    return result is None

@test
def extract_keyword_whitespace_only():
    """Test extraction with whitespace only message"""
    result = extract_keyword("   ")
    return result is None

@test
def extract_keyword_newlines():
    """Test extraction with newlines in message"""
    result = extract_keyword("Hello\n/u/xeqtbot dividend\nThanks")
    return result == "dividend"

@test
def extract_keyword_tabs():
    """Test extraction with tabs between trigger and keyword"""
    result = extract_keyword("/u/xeqtbot\tdividend")
    return result == "dividend"

@test
def extract_keyword_special_chars_in_keyword():
    """Test extraction with special characters in keyword (should fail)"""
    result = extract_keyword("/u/xeqtbot dividend-test")
    return result == "dividend"  # Should only capture the first word part

@test
def extract_keyword_numbers_in_keyword():
    """Test extraction with numbers in keyword"""
    result = extract_keyword("/u/xeqtbot test123")
    return result == "test123"

@test
def extract_keyword_underscore_in_keyword():
    """Test extraction with underscore in keyword"""
    result = extract_keyword("/u/xeqtbot test_keyword")
    return result == "test_keyword"

# ============================================================================
# CREATE_RESPONSE TESTS
# ============================================================================

@test
def create_response_known_keyword():
    """Test response creation for known keyword"""
    response = create_response("dividend")
    footer = read_file("./template/footer.md").strip()
    expected_faq = read_file("./faq/dividends.md").strip()
    expected = f"{expected_faq}\n\n{footer}"
    return response == expected

@test
def create_response_unknown_keyword():
    """Test response creation for unknown keyword"""
    response = create_response("nonexistent")
    footer = read_file("./template/footer.md").strip()
    expected_faq = read_file("./template/unknown.md").strip()
    expected = f"{expected_faq}\n\n{footer}"
    return response == expected

@test
def create_response_case_insensitive():
    """Test response creation with uppercase keyword"""
    response = create_response("DIVIDEND")
    footer = read_file("./template/footer.md").strip()
    expected_faq = read_file("./faq/dividends.md").strip()
    expected = f"{expected_faq}\n\n{footer}"
    return response == expected

@test
def create_response_multiple_keyword_mapping():
    """Test response creation for keyword that maps to same file as another"""
    response1 = create_response("lumpsum")
    response2 = create_response("dca")
    # Both should return the same content since they map to the same file
    return response1 == response2

@test
def create_response_distributions_keyword():
    """Test response creation for 'distributions' keyword"""
    response1 = create_response("dividend")
    response2 = create_response("distributions")
    # Both should return the same content since they map to the same file
    return response1 == response2

@test
def create_response_footer_appended():
    """Test that footer is properly appended"""
    response = create_response("dividend")
    footer = read_file("./template/footer.md").strip()
    return response.endswith(footer)

@test
def create_response_contains_faq_content():
    """Test that response contains FAQ content"""
    response = create_response("dividend")
    expected_faq = read_file("./faq/dividends.md").strip()
    return expected_faq in response

@test
def create_response_proper_formatting():
    """Test that response has proper formatting (FAQ + double newline + footer)"""
    response = create_response("dividend")
    parts = response.split("\n\n")
    # Should have at least 2 parts (FAQ content and footer)
    return len(parts) >= 2
