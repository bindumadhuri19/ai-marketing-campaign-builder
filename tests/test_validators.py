"""
Tests for validation utilities.
"""

import pytest
from utils.validators import (
    validate_url,
    extract_utm_params,
    detect_placeholders,
    url_in_text,
    check_character_limit
)


class TestURLValidation:
    """Test URL validation."""
    
    def test_valid_urls(self):
        """Test that valid URLs pass validation."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com/path?param=value") is True
        assert validate_url("https://sub.example.com/page") is True
    
    def test_invalid_urls(self):
        """Test that invalid URLs fail validation."""
        assert validate_url("not a url") is False
        assert validate_url("") is False
        assert validate_url("example.com") is False  # Missing scheme
    
    def test_url_with_utm(self):
        """Test URL with UTM parameters."""
        url = "https://example.com?utm_source=email&utm_medium=newsletter"
        assert validate_url(url) is True


class TestUTMExtraction:
    """Test UTM parameter extraction."""
    
    def test_extract_all_utm_params(self):
        """Test extraction of all UTM parameters."""
        url = "https://example.com?utm_source=email&utm_medium=newsletter&utm_campaign=launch"
        params = extract_utm_params(url)
        
        assert params["utm_source"] == "email"
        assert params["utm_medium"] == "newsletter"
        assert params["utm_campaign"] == "launch"
    
    def test_extract_partial_utm_params(self):
        """Test extraction with some UTM parameters missing."""
        url = "https://example.com?utm_source=email&other_param=value"
        params = extract_utm_params(url)
        
        assert params["utm_source"] == "email"
        assert "utm_medium" not in params
        assert "other_param" not in params
    
    def test_no_utm_params(self):
        """Test URL without UTM parameters."""
        url = "https://example.com?foo=bar"
        params = extract_utm_params(url)
        
        assert params == {}
    
    def test_empty_url(self):
        """Test empty URL."""
        params = extract_utm_params("")
        assert params == {}


class TestPlaceholderDetection:
    """Test placeholder detection."""
    
    def test_detect_double_braces(self):
        """Test detection of {{variable}} placeholders."""
        text = "Hello {{FIRST_NAME}}, welcome to {{COMPANY}}"
        placeholders = detect_placeholders(text)
        
        assert "{{FIRST_NAME}}" in placeholders
        assert "{{COMPANY}}" in placeholders
        assert len(placeholders) == 2
    
    def test_detect_square_brackets(self):
        """Test detection of [VARIABLE] placeholders."""
        text = "Dear [CUSTOMER_NAME], your [PRODUCT] is ready"
        placeholders = detect_placeholders(text)
        
        assert "[CUSTOMER_NAME]" in placeholders
        assert "[PRODUCT]" in placeholders
    
    def test_detect_curly_braces(self):
        """Test detection of {VARIABLE} placeholders."""
        text = "Hello {NAME}, thank you for {ACTION}"
        placeholders = detect_placeholders(text)
        
        assert "{NAME}" in placeholders
        assert "{ACTION}" in placeholders
    
    def test_mixed_placeholders(self):
        """Test detection of mixed placeholder types."""
        text = "Hi {{NAME}}, your [ORDER_ID] is {STATUS}"
        placeholders = detect_placeholders(text)
        
        assert len(placeholders) == 3
    
    def test_no_placeholders(self):
        """Test text without placeholders."""
        text = "Hello there, welcome to our service"
        placeholders = detect_placeholders(text)
        
        assert placeholders == []
    
    def test_lowercase_not_detected(self):
        """Test that lowercase {text} is not detected."""
        text = "Use curly braces {like this} for grouping"
        placeholders = detect_placeholders(text)
        
        # Should not detect lowercase
        assert len(placeholders) == 0


class TestURLInText:
    """Test URL presence in text."""
    
    def test_full_url_in_text(self):
        """Test that full URL is found in text."""
        url = "https://example.com/page"
        text = "Visit https://example.com/page for more info"
        
        assert url_in_text(url, text) is True
    
    def test_domain_in_text(self):
        """Test that domain is found even without full URL."""
        url = "https://example.com/page?utm_source=email"
        text = "Visit example.com for details"
        
        assert url_in_text(url, text) is True
    
    def test_url_not_in_text(self):
        """Test URL not present in text."""
        url = "https://example.com"
        text = "Visit our website for more information"
        
        assert url_in_text(url, text) is False
    
    def test_empty_inputs(self):
        """Test empty URL or text."""
        assert url_in_text("", "some text") is False
        assert url_in_text("https://example.com", "") is False


class TestCharacterLimit:
    """Test character limit checking."""
    
    def test_within_limit(self):
        """Test text within limit."""
        result = check_character_limit("Hello world", 20)
        
        assert result["passes"] is True
        assert result["count"] == 11
        assert result["limit"] == 20
    
    def test_exceeds_limit(self):
        """Test text exceeding limit."""
        result = check_character_limit("This is a very long text", 10)
        
        assert result["passes"] is False
        assert result["count"] == 24
        assert result["limit"] == 10
    
    def test_no_limit(self):
        """Test with no limit (None)."""
        result = check_character_limit("Any length text here", None)
        
        assert result["passes"] is True
        assert result["count"] == 20
        assert result["limit"] is None
    
    def test_empty_text(self):
        """Test empty text."""
        result = check_character_limit("", 10)
        
        assert result["passes"] is True
        assert result["count"] == 0
