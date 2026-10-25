"""
AI Marketing Campaign Builder & QA System
A Streamlit application for generating and validating marketing campaigns.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.constants import CHANNELS, DEMO_CAMPAIGNS, SEVERITY_OK, SEVERITY_WARNING, SEVERITY_ERROR
from utils.export import format_campaign_text, format_qa_report, format_campaign_json_pretty
from services.ai_service import get_ai_service
from services.qa_engine import get_qa_engine
from services.storage import get_storage

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Campaign Builder",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "current_campaign" not in st.session_state:
    st.session_state.current_campaign = None
if "qa_results" not in st.session_state:
    st.session_state.qa_results = None
if "demo_mode" not in st.session_state:
    demo_mode_env = os.getenv("DEMO_MODE", "false").lower()
    st.session_state.demo_mode = demo_mode_env == "true"


def main():
    """Main application entry point."""
    
    # Sidebar - Saved Campaigns
    with st.sidebar:
        st.header("📁 Saved Campaigns")
        
        storage = get_storage()
        saved_campaigns = storage.load_all_campaigns()
        
        if saved_campaigns:
            st.write(f"Total: {len(saved_campaigns)} campaigns")
            
            # Filter by status
            status_filter = st.selectbox(
                "Filter by status",
                options=["All", "approved", "draft", "rejected"]
            )
            
            # Apply filter
            if status_filter != "All":
                filtered_campaigns = [c for c in saved_campaigns if c.get("status") == status_filter]
            else:
                filtered_campaigns = saved_campaigns
            
            st.divider()
            
            # Display campaigns
            for camp in filtered_campaigns[:10]:  # Show max 10
                with st.expander(f"{camp.get('channel', 'Unknown')} - {camp.get('campaign_id', 'N/A')}"):
                    st.write(f"**Status:** {camp.get('status', 'unknown')}")
                    st.write(f"**Goal:** {camp.get('goal', 'N/A')}")
                    st.write(f"**Created:** {camp.get('created_at', 'N/A')[:10]}")
                    
                    if st.button("Load Campaign", key=f"load_{camp.get('campaign_id')}"):
                        st.session_state.current_campaign = camp
                        # Re-run QA checks
                        qa_engine = get_qa_engine()
                        qa_results = qa_engine.run_qa_checks(camp)
                        st.session_state.qa_results = qa_results
                        st.rerun()
        else:
            st.info("No saved campaigns yet")
    
    # Header
    st.title("📧 AI Marketing Campaign Builder & QA")
    st.markdown("""
    Generate marketing campaigns with AI assistance and automated quality checks.
    Supports Email and SMS channels with built-in validation.
    """)
    
    # Check for API configuration
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        st.warning("⚠ No API key configured. Running in demo mode with sample campaigns.")
        st.session_state.demo_mode = True
    
    # Display demo mode indicator
    if st.session_state.demo_mode:
        st.info("ℹ Demo Mode: Using sample campaigns. Configure ANTHROPIC_API_KEY in .env for AI generation.")
    
    # Main campaign creation form
    st.header("Create New Campaign")
    
    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            channel = st.radio(
                "Channel",
                options=list(CHANNELS.keys()),
                help="Select the marketing channel for this campaign"
            )
            
            goal = st.text_input(
                "Campaign Goal",
                placeholder="e.g., Drive demo signups, Increase webinar attendance",
                help="What is the primary objective of this campaign?"
            )
            
            audience = st.text_area(
                "Target Audience",
                placeholder="e.g., Tech-savvy marketing managers, Small business owners",
                help="Describe your target audience",
                height=100
            )
        
        with col2:
            cta = st.text_input(
                "Call-to-Action (CTA)",
                placeholder="e.g., Book Demo, Register Now, Learn More",
                help="The action you want recipients to take"
            )
            
            destination_url = st.text_input(
                "Destination URL",
                placeholder="https://example.com/page?utm_source=email&utm_medium=newsletter&utm_campaign=launch",
                help="Include UTM parameters for tracking (utm_source, utm_medium, utm_campaign)"
            )
            
            custom_message = st.text_area(
                "Additional Context (Optional)",
                placeholder="Any specific messaging points or requirements...",
                help="Provide additional context for the AI",
                height=100
            )
        
        submitted = st.form_submit_button("Generate Campaign", type="primary")
        
        if submitted:
            # Validate required fields
            if not all([channel, goal, audience, cta, destination_url]):
                st.error("Please fill in all required fields: Goal, Audience, CTA, and Destination URL")
            else:
                # Store inputs in session state
                st.session_state.campaign_inputs = {
                    "channel": channel,
                    "goal": goal,
                    "audience": audience,
                    "cta": cta,
                    "destination_url": destination_url,
                    "custom_message": custom_message
                }
                
                # Generate campaign with AI
                with st.spinner("Generating campaign through AI stages (Strategist → Content Creator → QA Reviewer)..."):
                    ai_service = get_ai_service()
                    campaign = ai_service.generate_campaign(
                        channel=channel,
                        goal=goal,
                        audience=audience,
                        cta=cta,
                        destination_url=destination_url,
                        custom_message=custom_message
                    )
                    st.session_state.current_campaign = campaign
                
                # Run automated QA checks (deterministic Python validation)
                with st.spinner("Running automated QA checks..."):
                    qa_engine = get_qa_engine()
                    qa_results = qa_engine.run_qa_checks(campaign)
                    st.session_state.qa_results = qa_results
    
    # Display generated campaign if available
    if st.session_state.current_campaign:
        campaign = st.session_state.current_campaign
        
        st.success("✓ Campaign generated successfully!")
        
        # Show demo mode warning if applicable
        if campaign.get("demo_mode"):
            st.warning("⚠ Demo mode: Using sample campaign. Configure API key for AI-generated content.")
        
        if campaign.get("error"):
            st.error(f"API Error (using demo fallback): {campaign['error']}")
        
        # Display AI Stages
        st.header("AI Generation Stages")
        
        with st.expander("Stage 1: Strategist", expanded=False):
            strategy = campaign.get("ai_stages", {}).get("strategy", {})
            st.write("**Strategy Overview:**")
            st.write(strategy.get("full_strategy", "N/A"))
        
        with st.expander("Stage 2: Content Creator", expanded=True):
            st.write("**Generated Campaign Content:**")
            
            if campaign["channel"] == "Email" and campaign.get("subject"):
                st.markdown(f"**Subject Line:** {campaign['subject']}")
                st.caption(f"Character count: {len(campaign['subject'])}/78")
            
            st.markdown("**Body:**")
            st.text_area(
                "Campaign Body",
                value=campaign.get("body", ""),
                height=200,
                key="campaign_body_display",
                disabled=True
            )
            
            body_length = len(campaign.get("body", ""))
            if campaign["channel"] == "SMS":
                st.caption(f"Character count: {body_length}/160")
            else:
                st.caption(f"Character count: {body_length}")
        
        with st.expander("Stage 3: QA Reviewer (AI Feedback)", expanded=False):
            qa_review = campaign.get("ai_stages", {}).get("qa_review", {})
            st.write("**AI Reviewer Feedback:**")
            st.info(qa_review.get("feedback", "No feedback available"))
        
        # Automated QA Checks (Deterministic Python)
        st.header("Automated QA Checks")
        
        if st.session_state.qa_results:
            qa_results = st.session_state.qa_results
            
            # Summary counts
            ok_count = sum(1 for r in qa_results if r["status"] == SEVERITY_OK)
            warn_count = sum(1 for r in qa_results if r["status"] == SEVERITY_WARNING)
            error_count = sum(1 for r in qa_results if r["status"] == SEVERITY_ERROR)
            
            # Summary row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Passed", ok_count, delta=None)
            with col2:
                st.metric("Warnings", warn_count, delta=None if warn_count == 0 else f"-{warn_count}")
            with col3:
                st.metric("Errors", error_count, delta=None if error_count == 0 else f"-{error_count}")
            
            st.divider()
            
            # Detailed results
            for result in qa_results:
                status = result["status"]
                check_name = result["check_name"]
                message = result["message"]
                
                # Visual indicator
                if status == SEVERITY_OK:
                    st.success(f"[OK] **{check_name}**: {message}")
                elif status == SEVERITY_WARNING:
                    st.warning(f"[WARN] **{check_name}**: {message}")
                else:  # ERROR
                    st.error(f"[ERROR] **{check_name}**: {message}")
        else:
            st.info("Generate a campaign to see automated QA results")
        
        # Review & Approval Section
        st.divider()
        st.header("Review & Approve Campaign")
        
        # Editable campaign content
        st.subheader("Edit Campaign (Optional)")
        
        edited_subject = None
        if campaign["channel"] == "Email" and campaign.get("subject"):
            edited_subject = st.text_input(
                "Subject Line",
                value=campaign["subject"],
                key="edit_subject"
            )
        
        edited_body = st.text_area(
            "Message Body",
            value=campaign.get("body", ""),
            height=200,
            key="edit_body"
        )
        
        # Update campaign with edits
        if edited_subject and edited_subject != campaign.get("subject"):
            campaign["subject"] = edited_subject
        if edited_body != campaign.get("body"):
            campaign["body"] = edited_body
        
        # QA Summary for approval decision
        st.subheader("Decision")
        if st.session_state.qa_results:
            qa_results = st.session_state.qa_results
            error_count = sum(1 for r in qa_results if r["status"] == SEVERITY_ERROR)
            warn_count = sum(1 for r in qa_results if r["status"] == SEVERITY_WARNING)
            
            if error_count > 0:
                st.warning(f"⚠ {error_count} error(s) detected. Review before approving.")
            elif warn_count > 0:
                st.info(f"ℹ {warn_count} warning(s). Consider addressing before approval.")
            else:
                st.success("✓ All QA checks passed!")
        
        # Approval buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        # Check for critical errors
        has_errors = False
        if st.session_state.qa_results:
            has_errors = any(r["status"] == SEVERITY_ERROR for r in st.session_state.qa_results)
        
        with col1:
            approve_button = st.button(
                "✓ Approve & Save", 
                type="primary",
                disabled=has_errors,
                help="Cannot approve campaigns with critical QA errors" if has_errors else "Mark campaign as approved and save"
            )
            if approve_button:
                storage = get_storage()
                campaign_id = storage.save_campaign(campaign, status="approved")
                st.success(f"Campaign approved and saved! ID: {campaign_id}")
                st.balloons()
        
        with col2:
            if st.button("📝 Save as Draft", type="secondary"):
                storage = get_storage()
                campaign_id = storage.save_campaign(campaign, status="draft")
                st.info(f"Campaign saved as draft. ID: {campaign_id}")
        
        with col3:
            if st.button("✗ Reject", type="secondary"):
                storage = get_storage()
                campaign_id = storage.save_campaign(campaign, status="rejected")
                st.warning(f"Campaign rejected and archived. ID: {campaign_id}")
        
        # Export & Download Section
        st.divider()
        st.subheader("Export Campaign")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as JSON
            json_data = format_campaign_json_pretty(campaign)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"campaign_{campaign.get('channel', 'unknown')}.json",
                mime="application/json",
                help="Download campaign data in JSON format"
            )
        
        with col2:
            # Download as formatted text
            text_data = format_campaign_text(campaign)
            st.download_button(
                label="📄 Download Campaign Text",
                data=text_data,
                file_name=f"campaign_{campaign.get('channel', 'unknown')}.txt",
                mime="text/plain",
                help="Download campaign in human-readable format"
            )
        
        with col3:
            # Download QA report
            if st.session_state.qa_results:
                qa_report = format_qa_report(campaign, st.session_state.qa_results)
                st.download_button(
                    label="📋 Download QA Report",
                    data=qa_report,
                    file_name=f"qa_report_{campaign.get('channel', 'unknown')}.txt",
                    mime="text/plain",
                    help="Download QA check results"
                )
        
        # Regenerate button
        st.divider()
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Regenerate Campaign", type="secondary"):
                if st.session_state.campaign_inputs:
                    with st.spinner("Regenerating..."):
                        inputs = st.session_state.campaign_inputs
                        ai_service = get_ai_service()
                        campaign = ai_service.generate_campaign(**inputs)
                        st.session_state.current_campaign = campaign
                        
                        # Re-run QA checks
                        qa_engine = get_qa_engine()
                        qa_results = qa_engine.run_qa_checks(campaign)
                        st.session_state.qa_results = qa_results
                        st.rerun()


if __name__ == "__main__":
    main()
