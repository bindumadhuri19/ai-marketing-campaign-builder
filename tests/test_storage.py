"""
Tests for campaign storage service.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from services.storage import CampaignStorage


class TestCampaignStorage:
    """Test suite for campaign storage."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = CampaignStorage(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_campaign(self):
        """Test saving a campaign."""
        campaign = {
            "channel": "Email",
            "subject": "Test Subject",
            "body": "Test body content",
            "goal": "Test goal",
            "audience": "Test audience",
            "cta": "Test CTA",
            "destination_url": "https://example.com"
        }
        
        campaign_id = self.storage.save_campaign(campaign, status="draft")
        
        # Verify campaign ID is generated
        assert campaign_id.startswith("campaign_")
        
        # Verify file exists
        file_path = Path(self.temp_dir) / f"{campaign_id}.json"
        assert file_path.exists()
        
        # Verify file content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["channel"] == "Email"
            assert saved_data["status"] == "draft"
            assert saved_data["campaign_id"] == campaign_id
            assert "created_at" in saved_data
            assert "updated_at" in saved_data
    
    def test_load_campaign(self):
        """Test loading a campaign."""
        campaign = {
            "channel": "SMS",
            "body": "Test SMS",
            "goal": "Test",
            "cta": "Click"
        }
        
        campaign_id = self.storage.save_campaign(campaign, status="approved")
        loaded = self.storage.load_campaign(campaign_id)
        
        assert loaded is not None
        assert loaded["channel"] == "SMS"
        assert loaded["status"] == "approved"
        assert loaded["campaign_id"] == campaign_id
    
    def test_load_nonexistent_campaign(self):
        """Test loading a campaign that doesn't exist."""
        loaded = self.storage.load_campaign("nonexistent_id")
        assert loaded is None
    
    def test_load_all_campaigns(self):
        """Test loading all campaigns."""
        # Save multiple campaigns
        campaign1 = {"channel": "Email", "status": "draft"}
        campaign2 = {"channel": "SMS", "status": "approved"}
        campaign3 = {"channel": "Email", "status": "rejected"}
        
        self.storage.save_campaign(campaign1, status="draft")
        self.storage.save_campaign(campaign2, status="approved")
        self.storage.save_campaign(campaign3, status="rejected")
        
        all_campaigns = self.storage.load_all_campaigns()
        
        assert len(all_campaigns) == 3
        
        # Verify all campaigns have required fields
        for camp in all_campaigns:
            assert "campaign_id" in camp
            assert "status" in camp
            assert "created_at" in camp
    
    def test_campaigns_sorted_by_date(self):
        """Test that campaigns are sorted by creation date (newest first)."""
        import time
        
        # Save campaigns with slight delay
        id1 = self.storage.save_campaign({"channel": "Email"}, "draft")
        time.sleep(0.1)
        id2 = self.storage.save_campaign({"channel": "SMS"}, "draft")
        time.sleep(0.1)
        id3 = self.storage.save_campaign({"channel": "Email"}, "draft")
        
        all_campaigns = self.storage.load_all_campaigns()
        
        # Newest should be first
        assert all_campaigns[0]["campaign_id"] == id3
        assert all_campaigns[1]["campaign_id"] == id2
        assert all_campaigns[2]["campaign_id"] == id1
    
    def test_update_campaign_status(self):
        """Test updating campaign status."""
        campaign = {"channel": "Email"}
        campaign_id = self.storage.save_campaign(campaign, status="draft")
        
        # Update status
        success = self.storage.update_campaign_status(campaign_id, "approved")
        assert success is True
        
        # Verify update
        loaded = self.storage.load_campaign(campaign_id)
        assert loaded["status"] == "approved"
        assert "updated_at" in loaded
    
    def test_update_nonexistent_campaign(self):
        """Test updating a campaign that doesn't exist."""
        success = self.storage.update_campaign_status("nonexistent", "approved")
        assert success is False
    
    def test_delete_campaign(self):
        """Test deleting a campaign."""
        campaign = {"channel": "Email"}
        campaign_id = self.storage.save_campaign(campaign, status="draft")
        
        # Verify file exists
        file_path = Path(self.temp_dir) / f"{campaign_id}.json"
        assert file_path.exists()
        
        # Delete campaign
        success = self.storage.delete_campaign(campaign_id)
        assert success is True
        
        # Verify file deleted
        assert not file_path.exists()
        
        # Verify campaign can't be loaded
        loaded = self.storage.load_campaign(campaign_id)
        assert loaded is None
    
    def test_delete_nonexistent_campaign(self):
        """Test deleting a campaign that doesn't exist."""
        success = self.storage.delete_campaign("nonexistent")
        assert success is False
    
    def test_storage_directory_created(self):
        """Test that storage directory is created if it doesn't exist."""
        new_dir = Path(self.temp_dir) / "new_campaigns"
        storage = CampaignStorage(storage_dir=str(new_dir))
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_save_with_unicode_content(self):
        """Test saving campaign with unicode characters."""
        campaign = {
            "channel": "Email",
            "subject": "Special offer: 50% off! 🎉",
            "body": "Get €100 discount today! © 2024"
        }
        
        campaign_id = self.storage.save_campaign(campaign, status="draft")
        loaded = self.storage.load_campaign(campaign_id)
        
        assert loaded["subject"] == "Special offer: 50% off! 🎉"
        assert "€100" in loaded["body"]
