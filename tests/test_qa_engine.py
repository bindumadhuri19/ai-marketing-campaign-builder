"""
Tests for QA engine.
"""

import pytest
from services.qa_engine import QAEngine, get_qa_engine
from utils.constants import SEVERITY_OK, SEVERITY_WARNING, SEVERITY_ERROR


class TestQAEngine:
    """Test suite for QA engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.qa_engine = QAEngine()
    
    def test_all_checks_pass(self):
        """Test campaign that passes all checks."""
        campaign = {
            "channel": "Email",
            "subject": "Transform Your Marketing with AI",
            "body": "Book a demo at https://example.com/demo?utm_source=email&utm_medium=newsletter&utm_campaign=launch to see how we can help.",
            "cta": "Book a demo",
            "destination_url": "https://example.com/demo?utm_source=email&utm_medium=newsletter&utm_campaign=launch"
        }
        
        results = self.qa_engine.run_qa_checks(campaign)
        
        # Should have multiple checks
        assert len(results) > 0
        
        # All should pass
        errors = [r for r in results if r["status"] == SEVERITY_ERROR]
        assert len(errors) == 0
    
    def test_cta_presence_check_pass(self):
        """Test CTA presence check when CTA is in body."""
        campaign = {
            "channel": "Email",
            "subject": "Test",
            "body": "Click here to book demo now!",
            "cta": "book demo",
            "destination_url": "https://example.com"
        }
        
        result = self.qa_engine._check_cta_presence(
            campaign["cta"], 
            campaign["body"]
        )
        
        assert result["status"] == SEVERITY_OK
        assert "found" in result["message"].lower()
    
    def test_cta_presence_check_fail(self):
        """Test CTA presence check when CTA is missing."""
        result = self.qa_engine._check_cta_presence(
            "Register Now",
            "Click here to learn more"
        )
        
        assert result["status"] == SEVERITY_WARNING
        assert "not found" in result["message"].lower()
    
    def test_url_format_valid(self):
        """Test URL format check with valid URL."""
        result = self.qa_engine._check_url_format(
            "https://example.com/page?param=value"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_url_format_invalid(self):
        """Test URL format check with invalid URL."""
        result = self.qa_engine._check_url_format("not-a-url")
        
        assert result["status"] == SEVERITY_ERROR
    
    def test_url_format_empty(self):
        """Test URL format check with empty URL."""
        result = self.qa_engine._check_url_format("")
        
        assert result["status"] == SEVERITY_ERROR
    
    def test_utm_parameters_all_present(self):
        """Test UTM check when all required parameters present."""
        url = "https://example.com?utm_source=email&utm_medium=newsletter&utm_campaign=launch"
        result = self.qa_engine._check_utm_parameters(url)
        
        assert result["status"] == SEVERITY_OK
        assert "all required" in result["message"].lower()
    
    def test_utm_parameters_missing(self):
        """Test UTM check when parameters are missing."""
        url = "https://example.com?utm_source=email"
        result = self.qa_engine._check_utm_parameters(url)
        
        assert result["status"] == SEVERITY_WARNING
        assert "missing" in result["message"].lower()
    
    def test_utm_parameters_none(self):
        """Test UTM check when no parameters present."""
        url = "https://example.com"
        result = self.qa_engine._check_utm_parameters(url)
        
        assert result["status"] == SEVERITY_ERROR
        assert "no utm" in result["message"].lower()
    
    def test_placeholder_detection_found(self):
        """Test placeholder detection when placeholders exist."""
        result = self.qa_engine._check_placeholders(
            subject="Hello {{NAME}}",
            body="Your order [ORDER_ID] is ready"
        )
        
        assert result["status"] == SEVERITY_ERROR
        assert "{{NAME}}" in result["message"]
        assert "[ORDER_ID]" in result["message"]
    
    def test_placeholder_detection_none(self):
        """Test placeholder detection when no placeholders."""
        result = self.qa_engine._check_placeholders(
            subject="Hello there",
            body="Your order is ready"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_email_subject_length_ok(self):
        """Test email subject length within limit."""
        result = self.qa_engine._check_email_subject_length(
            "Short subject line"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_email_subject_length_exceeds(self):
        """Test email subject length exceeding limit."""
        long_subject = "This is a very long subject line that definitely exceeds the recommended seventy-eight character limit"
        result = self.qa_engine._check_email_subject_length(long_subject)
        
        assert result["status"] == SEVERITY_WARNING
    
    def test_sms_body_length_ok(self):
        """Test SMS body length within limit."""
        result = self.qa_engine._check_sms_body_length(
            "Short SMS message"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_sms_body_length_exceeds(self):
        """Test SMS body length exceeding limit."""
        long_sms = "A" * 161  # 161 characters
        result = self.qa_engine._check_sms_body_length(long_sms)
        
        assert result["status"] == SEVERITY_ERROR
        assert "exceeds" in result["message"].lower()
    
    def test_link_in_body_found(self):
        """Test link presence when URL is in body."""
        result = self.qa_engine._check_link_in_body(
            url="https://example.com/page",
            body="Visit https://example.com/page for more info"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_link_in_body_domain_only(self):
        """Test link presence when only domain is in body."""
        result = self.qa_engine._check_link_in_body(
            url="https://example.com/page?param=value",
            body="Visit example.com for more"
        )
        
        assert result["status"] == SEVERITY_OK
    
    def test_link_in_body_not_found(self):
        """Test link presence when URL not in body."""
        result = self.qa_engine._check_link_in_body(
            url="https://example.com",
            body="Visit our website"
        )
        
        assert result["status"] == SEVERITY_WARNING
    
    def test_sms_campaign_checks(self):
        """Test QA checks for SMS campaign."""
        campaign = {
            "channel": "SMS",
            "subject": None,
            "body": "Get 50% off! Visit example.com?utm_source=sms&utm_medium=text&utm_campaign=sale",
            "cta": "Get 50% off",
            "destination_url": "https://example.com?utm_source=sms&utm_medium=text&utm_campaign=sale"
        }
        
        results = self.qa_engine.run_qa_checks(campaign)
        
        # Should have SMS-specific checks
        assert any("SMS Body Length" in r["check_name"] for r in results)
        # Should not have email subject check
        assert not any("Subject Length" in r["check_name"] for r in results)
    
    def test_email_campaign_checks(self):
        """Test QA checks for Email campaign."""
        campaign = {
            "channel": "Email",
            "subject": "Great Offer Inside",
            "body": "Check out our deals at https://example.com",
            "cta": "Check out",
            "destination_url": "https://example.com"
        }
        
        results = self.qa_engine.run_qa_checks(campaign)
        
        # Should have email subject check
        assert any("Subject Length" in r["check_name"] for r in results)
        # Should not have SMS body check
        assert not any("SMS Body Length" in r["check_name"] for r in results)
    
    def test_singleton_pattern(self):
        """Test that get_qa_engine returns singleton."""
        engine1 = get_qa_engine()
        engine2 = get_qa_engine()
        assert engine1 is engine2
