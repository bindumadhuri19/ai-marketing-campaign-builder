"""
Tests for export utilities.
"""

import pytest
import json
from utils.export import format_campaign_text, format_qa_report, format_campaign_json_pretty


class TestCampaignTextExport:
    """Test campaign text formatting."""
    
    def test_format_email_campaign(self):
        """Test formatting of email campaign."""
        campaign = {
            "channel": "Email",
            "goal": "Drive demo signups",
            "audience": "Marketing managers",
            "cta": "Book Demo",
            "destination_url": "https://example.com/demo",
            "subject": "Transform Your Marketing",
            "body": "Check out our AI-powered solution.\n\nBook a demo today!",
            "campaign_id": "campaign_123",
            "status": "approved"
        }
        
        text = format_campaign_text(campaign)
        
        # Verify key components present
        assert "CAMPAIGN: Email" in text
        assert "Drive demo signups" in text
        assert "Transform Your Marketing" in text
        assert "Book a demo today!" in text
        assert "campaign_123" in text
        assert "approved" in text
    
    def test_format_sms_campaign(self):
        """Test formatting of SMS campaign (no subject)."""
        campaign = {
            "channel": "SMS",
            "goal": "Event registration",
            "audience": "Tech enthusiasts",
            "cta": "Register",
            "destination_url": "https://example.com/event",
            "body": "Register now for our event!",
            "subject": None
        }
        
        text = format_campaign_text(campaign)
        
        # Verify SMS-specific formatting
        assert "CAMPAIGN: SMS" in text
        assert "Event registration" in text
        assert "Register now for our event!" in text
        # Subject should not appear for SMS
        assert "Subject Line:" not in text


class TestQAReportExport:
    """Test QA report formatting."""
    
    def test_format_qa_report_all_pass(self):
        """Test QA report when all checks pass."""
        campaign = {
            "channel": "Email",
            "goal": "Test goal",
            "campaign_id": "campaign_456"
        }
        
        qa_results = [
            {"check_name": "CTA Presence", "status": "OK", "message": "CTA found"},
            {"check_name": "URL Format", "status": "OK", "message": "Valid URL"},
            {"check_name": "UTM Parameters", "status": "OK", "message": "All UTM params present"}
        ]
        
        report = format_qa_report(campaign, qa_results)
        
        # Verify report structure
        assert "CAMPAIGN QA REPORT" in report
        assert "campaign_456" in report
        assert "Total Checks: 3" in report
        assert "Passed: 3" in report
        assert "Warnings: 0" in report
        assert "Errors: 0" in report
        assert "Overall Status: PASSED" in report
        
        # Verify individual checks
        assert "[OK] CTA Presence" in report
        assert "[OK] URL Format" in report
    
    def test_format_qa_report_with_warnings(self):
        """Test QA report with warnings."""
        campaign = {
            "channel": "Email",
            "goal": "Test"
        }
        
        qa_results = [
            {"check_name": "CTA Presence", "status": "OK", "message": "CTA found"},
            {"check_name": "UTM Parameters", "status": "WARN", "message": "Missing utm_campaign"}
        ]
        
        report = format_qa_report(campaign, qa_results)
        
        assert "Passed: 1" in report
        assert "Warnings: 1" in report
        assert "Errors: 0" in report
        assert "PASSED WITH WARNINGS" in report
        assert "[WARN] UTM Parameters" in report
    
    def test_format_qa_report_with_errors(self):
        """Test QA report with errors."""
        campaign = {
            "channel": "Email",
            "goal": "Test"
        }
        
        qa_results = [
            {"check_name": "URL Format", "status": "ERROR", "message": "Invalid URL"},
            {"check_name": "Placeholder Detection", "status": "ERROR", "message": "Found {{NAME}}"}
        ]
        
        report = format_qa_report(campaign, qa_results)
        
        assert "Passed: 0" in report
        assert "Warnings: 0" in report
        assert "Errors: 2" in report
        assert "Overall Status: FAILED" in report
        assert "[ERROR] URL Format" in report
        assert "[ERROR] Placeholder Detection" in report


class TestJSONExport:
    """Test JSON export formatting."""
    
    def test_format_campaign_json(self):
        """Test JSON formatting."""
        campaign = {
            "channel": "Email",
            "subject": "Test Subject",
            "body": "Test body",
            "goal": "Test goal"
        }
        
        json_str = format_campaign_json_pretty(campaign)
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["channel"] == "Email"
        assert parsed["subject"] == "Test Subject"
        
        # Verify it's formatted (has newlines for readability)
        assert "\n" in json_str
        assert "  " in json_str  # Indentation
    
    def test_json_with_unicode(self):
        """Test JSON export with unicode characters."""
        campaign = {
            "channel": "Email",
            "subject": "Special offer: €100 off! 🎉",
            "body": "Get 50% discount today © 2024"
        }
        
        json_str = format_campaign_json_pretty(campaign)
        
        # Verify unicode is preserved
        assert "€100" in json_str
        assert "🎉" in json_str
        assert "©" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "€100" in parsed["subject"]
