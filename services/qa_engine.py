"""
QA Engine for automated campaign quality checks.
Performs deterministic Python-based validation (not AI-based).
"""

from typing import Dict, List
from utils.validators import (
    validate_url,
    extract_utm_params,
    detect_placeholders,
    url_in_text,
    check_character_limit
)
from utils.constants import (
    CHANNELS,
    REQUIRED_UTM_PARAMS,
    SEVERITY_OK,
    SEVERITY_WARNING,
    SEVERITY_ERROR
)


class QAEngine:
    """
    Automated QA engine for campaign validation.
    All checks are deterministic Python logic (not AI).
    """
    
    def run_qa_checks(self, campaign: Dict) -> List[Dict]:
        """
        Run all QA checks on a campaign.
        
        Args:
            campaign: Campaign dict with channel, subject, body, cta, destination_url
        
        Returns:
            List of QA check results, each with:
            - check_name: Name of the check
            - status: SEVERITY_OK, SEVERITY_WARNING, or SEVERITY_ERROR
            - message: Human-readable result message
            - severity: Same as status (for backward compatibility)
        """
        results = []
        
        channel = campaign.get("channel", "Email")
        subject = campaign.get("subject", "")
        body = campaign.get("body", "")
        cta = campaign.get("cta", "")
        destination_url = campaign.get("destination_url", "")
        
        # Check 1: CTA Presence
        results.append(self._check_cta_presence(cta, body))
        
        # Check 2: URL Validation
        results.append(self._check_url_format(destination_url))
        
        # Check 3: UTM Parameters
        results.append(self._check_utm_parameters(destination_url))
        
        # Check 4: Placeholder Detection
        results.append(self._check_placeholders(subject, body))
        
        # Check 5: Character Limits
        if channel == "Email":
            results.append(self._check_email_subject_length(subject))
        elif channel == "SMS":
            results.append(self._check_sms_body_length(body))
        
        # Check 6: Link in Body
        results.append(self._check_link_in_body(destination_url, body))
        
        return results
    
    def _check_cta_presence(self, cta: str, body: str) -> Dict:
        """Check if CTA text appears in message body."""
        if not cta:
            return {
                "check_name": "CTA Presence",
                "status": SEVERITY_WARNING,
                "message": "No CTA specified",
                "severity": SEVERITY_WARNING
            }
        
        # Case-insensitive search
        if cta.lower() in body.lower():
            return {
                "check_name": "CTA Presence",
                "status": SEVERITY_OK,
                "message": f"CTA '{cta}' found in message body",
                "severity": SEVERITY_OK
            }
        else:
            return {
                "check_name": "CTA Presence",
                "status": SEVERITY_WARNING,
                "message": f"CTA '{cta}' not found in message body",
                "severity": SEVERITY_WARNING
            }
    
    def _check_url_format(self, url: str) -> Dict:
        """Validate destination URL format."""
        if not url:
            return {
                "check_name": "URL Format",
                "status": SEVERITY_ERROR,
                "message": "No destination URL provided",
                "severity": SEVERITY_ERROR
            }
        
        if validate_url(url):
            return {
                "check_name": "URL Format",
                "status": SEVERITY_OK,
                "message": "Valid URL format",
                "severity": SEVERITY_OK
            }
        else:
            return {
                "check_name": "URL Format",
                "status": SEVERITY_ERROR,
                "message": f"Invalid URL format: {url}",
                "severity": SEVERITY_ERROR
            }
    
    def _check_utm_parameters(self, url: str) -> Dict:
        """Check for required UTM tracking parameters."""
        if not url:
            return {
                "check_name": "UTM Parameters",
                "status": SEVERITY_ERROR,
                "message": "No URL to check for UTM parameters",
                "severity": SEVERITY_ERROR
            }
        
        utm_params = extract_utm_params(url)
        
        if not utm_params:
            return {
                "check_name": "UTM Parameters",
                "status": SEVERITY_ERROR,
                "message": "No UTM parameters found in URL",
                "severity": SEVERITY_ERROR
            }
        
        # Check for required params
        missing_params = []
        for param in REQUIRED_UTM_PARAMS:
            if param not in utm_params:
                missing_params.append(param)
        
        if missing_params:
            return {
                "check_name": "UTM Parameters",
                "status": SEVERITY_WARNING,
                "message": f"Missing UTM parameters: {', '.join(missing_params)}",
                "severity": SEVERITY_WARNING
            }
        
        return {
            "check_name": "UTM Parameters",
            "status": SEVERITY_OK,
            "message": f"All required UTM parameters present: {', '.join(utm_params.keys())}",
            "severity": SEVERITY_OK
        }
    
    def _check_placeholders(self, subject: str, body: str) -> Dict:
        """Detect unreplaced placeholder text."""
        combined_text = f"{subject or ''} {body or ''}"
        placeholders = detect_placeholders(combined_text)
        
        if placeholders:
            return {
                "check_name": "Placeholder Detection",
                "status": SEVERITY_ERROR,
                "message": f"Unreplaced placeholders found: {', '.join(set(placeholders))}",
                "severity": SEVERITY_ERROR
            }
        
        return {
            "check_name": "Placeholder Detection",
            "status": SEVERITY_OK,
            "message": "No placeholders detected",
            "severity": SEVERITY_OK
        }
    
    def _check_email_subject_length(self, subject: str) -> Dict:
        """Check email subject line character limit."""
        limit = CHANNELS["Email"]["subject_max_length"]
        check = check_character_limit(subject, limit)
        
        if check["passes"]:
            return {
                "check_name": "Subject Length",
                "status": SEVERITY_OK,
                "message": f"Subject line within limit ({check['count']}/{limit} characters)",
                "severity": SEVERITY_OK
            }
        else:
            return {
                "check_name": "Subject Length",
                "status": SEVERITY_WARNING,
                "message": f"Subject line exceeds recommended limit ({check['count']}/{limit} characters)",
                "severity": SEVERITY_WARNING
            }
    
    def _check_sms_body_length(self, body: str) -> Dict:
        """Check SMS body character limit."""
        limit = CHANNELS["SMS"]["body_max_length"]
        check = check_character_limit(body, limit)
        
        if check["passes"]:
            return {
                "check_name": "SMS Body Length",
                "status": SEVERITY_OK,
                "message": f"SMS body within limit ({check['count']}/{limit} characters)",
                "severity": SEVERITY_OK
            }
        else:
            return {
                "check_name": "SMS Body Length",
                "status": SEVERITY_ERROR,
                "message": f"SMS body exceeds limit ({check['count']}/{limit} characters)",
                "severity": SEVERITY_ERROR
            }
    
    def _check_link_in_body(self, url: str, body: str) -> Dict:
        """Check if destination URL appears in message body."""
        if not url:
            return {
                "check_name": "Link in Body",
                "status": SEVERITY_WARNING,
                "message": "No destination URL to verify",
                "severity": SEVERITY_WARNING
            }
        
        if url_in_text(url, body):
            return {
                "check_name": "Link in Body",
                "status": SEVERITY_OK,
                "message": "Destination URL found in message body",
                "severity": SEVERITY_OK
            }
        else:
            return {
                "check_name": "Link in Body",
                "status": SEVERITY_WARNING,
                "message": "Destination URL not found in message body (may need to be added)",
                "severity": SEVERITY_WARNING
            }


# Singleton instance
_qa_engine = None

def get_qa_engine() -> QAEngine:
    """Get or create QA engine singleton."""
    global _qa_engine
    if _qa_engine is None:
        _qa_engine = QAEngine()
    return _qa_engine
