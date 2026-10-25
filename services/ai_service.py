"""
AI service for campaign generation using Anthropic Claude.
Implements three-stage workflow: Strategist -> Content Creator -> QA Reviewer.
"""

import os
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from utils.constants import CHANNELS, DEMO_CAMPAIGNS

# Load environment variables
load_dotenv()


class CampaignAIService:
    """
    AI service with three-stage campaign generation:
    1. Strategist: Analyzes inputs and creates campaign strategy
    2. Content Creator: Generates campaign copy based on strategy
    3. QA Reviewer: Reviews content and provides suggestions
    """
    
    def __init__(self):
        """Initialize AI service with configurable model."""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        # Only initialize client if API key is available
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None
            self.demo_mode = True
    
    def generate_campaign(
        self,
        channel: str,
        goal: str,
        audience: str,
        cta: str,
        destination_url: str,
        custom_message: Optional[str] = None
    ) -> Dict:
        """
        Generate a marketing campaign through three AI stages.
        
        Args:
            channel: Email or SMS
            goal: Campaign objective
            audience: Target audience description
            cta: Call-to-action text
            destination_url: Landing page URL
            custom_message: Optional additional context
        
        Returns:
            Dict with campaign data including subject (if Email), body, and AI stages
        """
        # Demo mode: Return sample campaign
        if self.demo_mode or not self.client:
            return self._get_demo_campaign(channel, goal, audience, cta, destination_url)
        
        try:
            # Stage 1: Strategist
            strategy = self._run_strategist(channel, goal, audience, cta, custom_message)
            
            # Stage 2: Content Creator
            content = self._run_content_creator(
                channel, goal, audience, cta, destination_url, strategy, custom_message
            )
            
            # Stage 3: QA Reviewer
            qa_review = self._run_qa_reviewer(channel, content, goal, cta, destination_url)
            
            # Combine results
            campaign = {
                "channel": channel,
                "goal": goal,
                "audience": audience,
                "cta": cta,
                "destination_url": destination_url,
                "subject": content.get("subject"),
                "body": content.get("body"),
                "ai_stages": {
                    "strategy": strategy,
                    "content": content,
                    "qa_review": qa_review
                },
                "status": "draft"
            }
            
            return campaign
            
        except Exception as e:
            # Fallback to demo mode on error
            print(f"AI generation error: {e}")
            return self._get_demo_campaign(
                channel, goal, audience, cta, destination_url, 
                error_message=str(e)
            )
    
    def _run_strategist(
        self, 
        channel: str, 
        goal: str, 
        audience: str, 
        cta: str, 
        custom_message: Optional[str]
    ) -> Dict:
        """
        Stage 1: Strategist - Analyze inputs and create campaign strategy.
        """
        prompt = f"""You are a marketing strategist. Analyze these campaign requirements and create a strategic approach.

Channel: {channel}
Goal: {goal}
Audience: {audience}
Call-to-Action: {cta}
{f'Additional Context: {custom_message}' if custom_message else ''}

Provide a brief strategy covering:
1. Key message positioning (1-2 sentences)
2. Tone and style recommendation
3. Primary value proposition to emphasize

Keep your response concise and actionable."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        strategy_text = response.content[0].text
        
        return {
            "positioning": strategy_text.split('\n')[0] if strategy_text else "",
            "full_strategy": strategy_text
        }
    
    def _run_content_creator(
        self,
        channel: str,
        goal: str,
        audience: str,
        cta: str,
        destination_url: str,
        strategy: Dict,
        custom_message: Optional[str]
    ) -> Dict:
        """
        Stage 2: Content Creator - Generate campaign copy based on strategy.
        """
        channel_config = CHANNELS[channel]
        
        # Build prompt based on channel requirements
        if channel == "Email":
            prompt = f"""You are a marketing copywriter. Create an email campaign based on this strategy:

STRATEGY:
{strategy['full_strategy']}

REQUIREMENTS:
- Goal: {goal}
- Audience: {audience}
- Call-to-Action: "{cta}" (MUST include this exact phrase in the body)
- Destination URL: {destination_url} (MUST use this EXACT URL without modification)
- Subject line: Max {channel_config['subject_max_length']} characters
{f'- Additional Context: {custom_message}' if custom_message else ''}

CRITICAL RULES:
1. Include the exact CTA phrase "{cta}" in the message body
2. Include the EXACT destination URL: {destination_url}
3. Do NOT modify, shorten, or reformat the URL
4. Do NOT make unverified quantitative claims (e.g., "reduce by X%")

Generate:
1. Subject line (compelling, under {channel_config['subject_max_length']} chars)
2. Email body (3-4 short paragraphs, include CTA and exact URL)

Format your response as:
SUBJECT: [subject line]
BODY:
[email body text]"""
        
        else:  # SMS
            prompt = f"""You are a marketing copywriter. Create an SMS campaign based on this strategy:

STRATEGY:
{strategy['full_strategy']}

REQUIREMENTS:
- Goal: {goal}
- Audience: {audience}
- Call-to-Action: "{cta}" (MUST include this exact phrase)
- Destination URL: {destination_url} (MUST use this EXACT URL)
- Character limit: {channel_config['body_max_length']} characters total
{f'- Additional Context: {custom_message}' if custom_message else ''}

CRITICAL RULES:
1. Include the exact CTA phrase "{cta}" in the message
2. Include the EXACT destination URL: {destination_url}
3. Do NOT modify, shorten, or reformat the URL
4. Do NOT make unverified quantitative claims

Generate a concise SMS message (under {channel_config['body_max_length']} chars) that includes:
- Clear value proposition
- Call-to-action phrase
- Exact URL as provided

Format as:
BODY:
[SMS text]"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content_text = response.content[0].text
        
        # Parse response
        result = {}
        if channel == "Email":
            if "SUBJECT:" in content_text:
                subject_part = content_text.split("SUBJECT:")[1].split("BODY:")[0].strip()
                result["subject"] = subject_part
            if "BODY:" in content_text:
                body_part = content_text.split("BODY:")[1].strip()
                result["body"] = body_part
        else:
            if "BODY:" in content_text:
                body_part = content_text.split("BODY:")[1].strip()
                result["body"] = body_part
            else:
                result["body"] = content_text.strip()
        
        return result
    
    def _run_qa_reviewer(
        self,
        channel: str,
        content: Dict,
        goal: str,
        cta: str,
        destination_url: str
    ) -> Dict:
        """
        Stage 3: QA Reviewer - Review content and provide improvement suggestions.
        Note: This is AI-based review. Deterministic Python checks happen in qa_engine.py.
        """
        channel_config = CHANNELS[channel]
        
        subject = content.get("subject", "N/A")
        body = content.get("body", "")
        
        prompt = f"""You are a marketing QA reviewer. Review this campaign content and provide suggestions.

CHANNEL: {channel}
GOAL: {goal}
EXPECTED CTA: {cta}
DESTINATION URL: {destination_url}

CONTENT:
{f'Subject: {subject}' if channel == 'Email' else ''}
Body: {body}

CHARACTER LIMITS:
{f'- Subject: {len(subject)}/{channel_config.get("subject_max_length", "N/A")} chars' if channel == 'Email' else ''}
- Body: {len(body)}/{channel_config.get("body_max_length", "N/A") or "unlimited"} chars

Provide brief feedback:
1. Does the content align with the goal?
2. Is the CTA clear and compelling?
3. Any suggestions for improvement?

Be concise (3-4 sentences total)."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "feedback": response.content[0].text,
            "reviewed": True
        }
    
    def _get_demo_campaign(
        self,
        channel: str,
        goal: str,
        audience: str,
        cta: str,
        destination_url: str,
        error_message: Optional[str] = None
    ) -> Dict:
        """
        Return a demo campaign when API is unavailable.
        """
        demo = DEMO_CAMPAIGNS.get(channel, DEMO_CAMPAIGNS["Email"])
        
        return {
            "channel": channel,
            "goal": goal,
            "audience": audience,
            "cta": cta,
            "destination_url": destination_url,
            "subject": demo.get("subject"),
            "body": demo.get("body"),
            "ai_stages": {
                "strategy": {
                    "positioning": "Demo mode - using sample campaign",
                    "full_strategy": "This is a sample campaign for demonstration purposes."
                },
                "content": {
                    "subject": demo.get("subject"),
                    "body": demo.get("body")
                },
                "qa_review": {
                    "feedback": "Demo mode active. Configure ANTHROPIC_API_KEY for AI-generated campaigns.",
                    "reviewed": False
                }
            },
            "status": "draft",
            "demo_mode": True,
            "error": error_message if error_message else None
        }


# Singleton instance
_ai_service = None

def get_ai_service() -> CampaignAIService:
    """Get or create AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = CampaignAIService()
    return _ai_service
