"""
Tests for AI service campaign generation.
"""

import pytest
from unittest.mock import Mock, patch
from services.ai_service import CampaignAIService, get_ai_service


class TestCampaignAIService:
    """Test suite for CampaignAIService."""
    
    def test_demo_mode_without_api_key(self):
        """Test that service falls back to demo mode without API key."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': '', 'DEMO_MODE': 'false'}):
            service = CampaignAIService()
            assert service.demo_mode is True
            assert service.client is None
    
    def test_demo_mode_explicit(self):
        """Test explicit demo mode setting."""
        with patch.dict('os.environ', {'DEMO_MODE': 'true'}):
            service = CampaignAIService()
            assert service.demo_mode is True
    
    def test_demo_campaign_email(self):
        """Test demo campaign generation for Email channel."""
        with patch.dict('os.environ', {'DEMO_MODE': 'true'}):
            service = CampaignAIService()
            campaign = service.generate_campaign(
                channel="Email",
                goal="Drive demo signups",
                audience="Marketing managers",
                cta="Book Demo",
                destination_url="https://example.com/demo?utm_source=email&utm_medium=newsletter&utm_campaign=launch"
            )
            
            # Verify structure
            assert campaign["channel"] == "Email"
            assert campaign["goal"] == "Drive demo signups"
            assert campaign["status"] == "draft"
            assert campaign.get("subject") is not None
            assert campaign.get("body") is not None
            assert campaign["demo_mode"] is True
            
            # Verify AI stages structure
            assert "ai_stages" in campaign
            assert "strategy" in campaign["ai_stages"]
            assert "content" in campaign["ai_stages"]
            assert "qa_review" in campaign["ai_stages"]
    
    def test_demo_campaign_sms(self):
        """Test demo campaign generation for SMS channel."""
        with patch.dict('os.environ', {'DEMO_MODE': 'true'}):
            service = CampaignAIService()
            campaign = service.generate_campaign(
                channel="SMS",
                goal="Event registration",
                audience="Tech enthusiasts",
                cta="Register Now",
                destination_url="https://example.com/register?utm_source=sms&utm_campaign=event"
            )
            
            # Verify structure
            assert campaign["channel"] == "SMS"
            assert campaign.get("subject") is None  # SMS has no subject
            assert campaign.get("body") is not None
            assert campaign["demo_mode"] is True
    
    def test_configurable_model(self):
        """Test that model is configurable via environment."""
        with patch.dict('os.environ', {'CLAUDE_MODEL': 'claude-3-opus-20240229'}):
            service = CampaignAIService()
            assert service.model == 'claude-3-opus-20240229'
    
    def test_model_default(self):
        """Test default model when not configured."""
        with patch.dict('os.environ', {}, clear=True):
            service = CampaignAIService()
            assert service.model == 'claude-3-5-sonnet-20241022'
    
    @patch('services.ai_service.Anthropic')
    def test_ai_generation_with_api_key(self, mock_anthropic):
        """Test AI generation with valid API key (mocked)."""
        # Mock API responses
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Mock strategist response
        mock_strategy_response = Mock()
        mock_strategy_response.content = [Mock(text="Focus on time-saving benefits.\nTone: Professional, conversational\nValue: Reduce QA time by 95%")]
        
        # Mock content creator response
        mock_content_response = Mock()
        mock_content_response.content = [Mock(text="SUBJECT: Save 15 hours per week on campaign QA\nBODY:\nHi there,\n\nTired of manual campaign checks?\n\nOur AI builder catches errors automatically.\n\nBook Demo https://example.com")]
        
        # Mock QA reviewer response
        mock_qa_response = Mock()
        mock_qa_response.content = [Mock(text="Content aligns well with goal. CTA is clear. Consider adding urgency.")]
        
        mock_client.messages.create.side_effect = [
            mock_strategy_response,
            mock_content_response,
            mock_qa_response
        ]
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-test-key', 'DEMO_MODE': 'false'}):
            service = CampaignAIService()
            campaign = service.generate_campaign(
                channel="Email",
                goal="Drive demo signups",
                audience="Marketing managers",
                cta="Book Demo",
                destination_url="https://example.com/demo"
            )
            
            # Verify AI was called
            assert mock_client.messages.create.call_count == 3
            
            # Verify campaign structure
            assert campaign["subject"] == "Save 15 hours per week on campaign QA"
            assert "Hi there" in campaign["body"]
            assert campaign.get("demo_mode") is None
            
            # Verify all stages completed
            assert campaign["ai_stages"]["strategy"]["positioning"]
            assert campaign["ai_stages"]["content"]["subject"]
            assert campaign["ai_stages"]["qa_review"]["feedback"]
            assert campaign["ai_stages"]["qa_review"]["reviewed"] is True
    
    def test_singleton_pattern(self):
        """Test that get_ai_service returns singleton."""
        service1 = get_ai_service()
        service2 = get_ai_service()
        assert service1 is service2


class TestAIServiceErrorHandling:
    """Test error handling in AI service."""
    
    @patch('services.ai_service.Anthropic')
    def test_api_error_fallback_to_demo(self, mock_anthropic):
        """Test fallback to demo mode when API fails."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API rate limit exceeded")
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-test-key', 'DEMO_MODE': 'false'}):
            service = CampaignAIService()
            campaign = service.generate_campaign(
                channel="Email",
                goal="Test",
                audience="Test",
                cta="Test",
                destination_url="https://test.com"
            )
            
            # Should fallback to demo mode
            assert campaign["demo_mode"] is True
            assert campaign["error"] is not None
            assert "API rate limit exceeded" in campaign["error"]
