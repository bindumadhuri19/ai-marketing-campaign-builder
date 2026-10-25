"""
Export utilities for campaign and QA report formatting.
"""

from typing import Dict, List
from datetime import datetime


def format_campaign_text(campaign: Dict) -> str:
    """
    Format campaign as human-readable text for copy-paste.
    
    Args:
        campaign: Campaign dict
    
    Returns:
        Formatted text string
    """
    channel = campaign.get("channel", "Unknown")
    lines = []
    
    # Header
    lines.append("=" * 60)
    lines.append(f"CAMPAIGN: {channel}")
    lines.append("=" * 60)
    lines.append("")
    
    # Metadata
    lines.append("CAMPAIGN DETAILS")
    lines.append("-" * 60)
    lines.append(f"Channel: {channel}")
    lines.append(f"Goal: {campaign.get('goal', 'N/A')}")
    lines.append(f"Audience: {campaign.get('audience', 'N/A')}")
    lines.append(f"CTA: {campaign.get('cta', 'N/A')}")
    lines.append(f"Destination URL: {campaign.get('destination_url', 'N/A')}")
    
    if campaign.get("campaign_id"):
        lines.append(f"Campaign ID: {campaign['campaign_id']}")
    if campaign.get("status"):
        lines.append(f"Status: {campaign['status']}")
    if campaign.get("created_at"):
        lines.append(f"Created: {campaign['created_at']}")
    
    lines.append("")
    
    # Content
    lines.append("CAMPAIGN CONTENT")
    lines.append("-" * 60)
    
    if channel == "Email" and campaign.get("subject"):
        lines.append(f"Subject Line:")
        lines.append(f"  {campaign['subject']}")
        lines.append("")
    
    lines.append("Message Body:")
    body = campaign.get("body", "")
    # Indent body for readability
    for line in body.split("\n"):
        lines.append(f"  {line}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_qa_report(campaign: Dict, qa_results: List[Dict]) -> str:
    """
    Format QA results as a readable report.
    
    Args:
        campaign: Campaign dict
        qa_results: List of QA check results
    
    Returns:
        Formatted QA report text
    """
    lines = []
    
    # Header
    lines.append("=" * 60)
    lines.append("CAMPAIGN QA REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # Campaign info
    lines.append(f"Campaign: {campaign.get('channel', 'Unknown')}")
    if campaign.get("campaign_id"):
        lines.append(f"ID: {campaign['campaign_id']}")
    lines.append(f"Goal: {campaign.get('goal', 'N/A')}")
    lines.append("")
    
    # Summary
    ok_count = sum(1 for r in qa_results if r["status"] == "OK")
    warn_count = sum(1 for r in qa_results if r["status"] == "WARN")
    error_count = sum(1 for r in qa_results if r["status"] == "ERROR")
    
    lines.append("QA SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Total Checks: {len(qa_results)}")
    lines.append(f"Passed: {ok_count}")
    lines.append(f"Warnings: {warn_count}")
    lines.append(f"Errors: {error_count}")
    lines.append("")
    
    # Overall status
    if error_count > 0:
        lines.append("Overall Status: FAILED (errors detected)")
    elif warn_count > 0:
        lines.append("Overall Status: PASSED WITH WARNINGS")
    else:
        lines.append("Overall Status: PASSED")
    
    lines.append("")
    
    # Detailed results
    lines.append("DETAILED RESULTS")
    lines.append("-" * 60)
    
    for result in qa_results:
        status = result["status"]
        check_name = result["check_name"]
        message = result["message"]
        
        lines.append(f"[{status}] {check_name}")
        lines.append(f"     {message}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_campaign_json_pretty(campaign: Dict) -> str:
    """
    Format campaign as pretty-printed JSON.
    
    Args:
        campaign: Campaign dict
    
    Returns:
        JSON string with indentation
    """
    import json
    return json.dumps(campaign, indent=2, ensure_ascii=False)
