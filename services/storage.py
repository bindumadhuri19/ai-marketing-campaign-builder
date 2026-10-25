"""
Storage service for campaign persistence using JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CampaignStorage:
    """Handles saving and loading campaigns from JSON files."""
    
    def __init__(self, storage_dir: str = "campaigns"):
        """
        Initialize storage service.
        
        Args:
            storage_dir: Directory path for storing campaign files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_campaign(self, campaign: Dict, status: str = "draft") -> str:
        """
        Save campaign to JSON file.
        
        Args:
            campaign: Campaign dict to save
            status: Campaign status (draft, approved, rejected)
        
        Returns:
            Campaign ID (filename without extension)
        """
        # Generate campaign ID from timestamp with microseconds for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        campaign_id = f"campaign_{timestamp}"
        
        # Update campaign with metadata
        campaign_data = {
            **campaign,
            "campaign_id": campaign_id,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to file
        file_path = self.storage_dir / f"{campaign_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(campaign_data, f, indent=2, ensure_ascii=False)
        
        return campaign_id
    
    def load_campaign(self, campaign_id: str) -> Optional[Dict]:
        """
        Load campaign from JSON file.
        
        Args:
            campaign_id: Campaign ID to load
        
        Returns:
            Campaign dict or None if not found
        """
        file_path = self.storage_dir / f"{campaign_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_campaigns(self) -> List[Dict]:
        """
        Load all campaigns from storage directory.
        
        Returns:
            List of campaign dicts, sorted by creation date (newest first)
        """
        campaigns = []
        
        for file_path in self.storage_dir.glob("campaign_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    campaign = json.load(f)
                    campaigns.append(campaign)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        # Sort by created_at timestamp (newest first)
        campaigns.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return campaigns
    
    def update_campaign_status(self, campaign_id: str, new_status: str) -> bool:
        """
        Update status of existing campaign.
        
        Args:
            campaign_id: Campaign ID to update
            new_status: New status value
        
        Returns:
            True if successful, False if campaign not found
        """
        campaign = self.load_campaign(campaign_id)
        
        if campaign is None:
            return False
        
        campaign["status"] = new_status
        campaign["updated_at"] = datetime.now().isoformat()
        
        file_path = self.storage_dir / f"{campaign_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(campaign, f, indent=2, ensure_ascii=False)
        
        return True
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete campaign file.
        
        Args:
            campaign_id: Campaign ID to delete
        
        Returns:
            True if successful, False if campaign not found
        """
        file_path = self.storage_dir / f"{campaign_id}.json"
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True


# Singleton instance
_storage = None

def get_storage() -> CampaignStorage:
    """Get or create storage singleton."""
    global _storage
    if _storage is None:
        _storage = CampaignStorage()
    return _storage
