"""
Constants and configuration for campaign builder.
"""

# Channel configurations
CHANNELS = {
    "Email": {
        "subject_max_length": 78,
        "body_max_length": None,  # No hard limit for email body
        "requires_subject": True,
        "display_name": "Email Campaign"
    },
    "SMS": {
        "subject_max_length": None,
        "body_max_length": 160,
        "requires_subject": False,
        "display_name": "SMS Campaign"
    }
}

# QA Check severity levels
SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARN"
SEVERITY_OK = "OK"

# UTM parameter requirements
REQUIRED_UTM_PARAMS = ["utm_source", "utm_medium", "utm_campaign"]

# Placeholder patterns (regex)
PLACEHOLDER_PATTERNS = [
    r'\{\{[^}]+\}\}',  # {{variable}}
    r'\[[A-Z_]+\]',    # [VARIABLE]
    r'\{[A-Z_]+\}',    # {VARIABLE}
]

# Campaign status options
STATUS_DRAFT = "draft"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

# Demo mode sample campaigns
DEMO_CAMPAIGNS = {
    "Email": {
        "subject": "Transform Your Marketing Operations with AI",
        "body": """Hi there,

Are you spending hours on campaign QA and still missing broken links?

Our AI-powered campaign builder helps marketing ops teams:
- Generate campaign copy in seconds
- Catch missing UTM parameters automatically
- Detect placeholder text before launch
- Ensure character limits for every channel

Book a demo today and streamline your campaign workflow.

[Book Demo] https://example.com/demo?utm_source=email&utm_medium=newsletter&utm_campaign=product_launch

Best regards,
The Campaign Builder Team"""
    },
    "SMS": {
        "subject": None,
        "body": "Ready to streamline your campaigns? Our AI builder catches errors before launch. Book demo: https://example.com/demo?utm_source=sms&utm_medium=text&utm_campaign=launch"
    }
}
