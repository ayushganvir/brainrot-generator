import json
import os
import logging
import requests
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.accounts_file = self.data_dir / "instagram_accounts.json"
        self.history_file = self.data_dir / "upload_history.json"
        
        self._load_data()

    def _load_data(self):
        """Load accounts and history from JSON files"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, 'r') as f:
                    self.accounts = json.load(f)
            except Exception as e:
                logger.error(f"Error loading accounts: {e}")
                self.accounts = {}
        else:
            self.accounts = {}

        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                self.history = []
        else:
            self.history = []

    def _save_accounts(self):
        """Save accounts to JSON file"""
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f, indent=2)

    def _save_history(self):
        """Save history to JSON file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_account(self, access_token, account_id, username):
        """Add or update an Instagram account"""
        self.accounts[account_id] = {
            "access_token": access_token,
            "username": username,
            "added_at": datetime.now().isoformat()
        }
        self._save_accounts()
        logger.info(f"Added Instagram account: {username} ({account_id})")
        return True

    def get_accounts(self):
        """Get list of linked accounts"""
        return [
            {"id": k, "username": v["username"], "added_at": v["added_at"]}
            for k, v in self.accounts.items()
        ]

    def remove_account(self, account_id):
        """Remove an account"""
        if account_id in self.accounts:
            del self.accounts[account_id]
            self._save_accounts()
            return True
        return False

    def upload_video(self, account_id, video_url, caption=""):
        """
        Upload video to Instagram (Reels) using Graph API
        Args:
            account_id: Instagram Business Account ID
            video_url: Publicly accessible URL of the video (required by Graph API)
            caption: Video caption
        """
        if account_id not in self.accounts:
            raise ValueError("Account not found")

        account = self.accounts[account_id]
        access_token = account["access_token"]
        
        logger.info(f"Starting upload to account {account['username']} ({account_id})")
        logger.info(f"Video URL: {video_url}")

        try:
            # Step 1: Create Media Container
            url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            payload = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": access_token
            }
            
            response = requests.post(url, json=payload)
            data = response.json()
            
            if "id" not in data:
                logger.error(f"Error creating media container: {data}")
                raise Exception(f"Failed to create media container: {data.get('error', {}).get('message', 'Unknown error')}")
                
            creation_id = data["id"]
            logger.info(f"Media container created: {creation_id}")

            # Step 2: Check Status (Wait for processing)
            import time
            status_url = f"https://graph.facebook.com/v18.0/{creation_id}"
            params = {
                "fields": "status_code",
                "access_token": access_token
            }
            
            max_retries = 20
            for i in range(max_retries):
                logger.info(f"Checking status (attempt {i+1}/{max_retries})...")
                status_res = requests.get(status_url, params=params)
                status_data = status_res.json()
                
                status_code = status_data.get("status_code")
                logger.info(f"Status: {status_code}")
                
                if status_code == "FINISHED":
                    break
                elif status_code == "ERROR":
                    raise Exception("Video processing failed on Instagram side")
                elif status_code == "IN_PROGRESS":
                    time.sleep(5) # Wait 5 seconds before next check
                else:
                    # EXPIRED or unknown
                    if i == max_retries - 1:
                        raise Exception("Timeout waiting for video processing")
                    time.sleep(5)

            # Step 3: Publish Media
            publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            
            publish_res = requests.post(publish_url, json=publish_payload)
            publish_data = publish_res.json()
            
            if "id" not in publish_data:
                logger.error(f"Error publishing media: {publish_data}")
                raise Exception(f"Failed to publish media: {publish_data.get('error', {}).get('message', 'Unknown error')}")
                
            media_id = publish_data["id"]
            permalink = f"https://www.instagram.com/p/{media_id}/" # We don't get permalink directly usually, but can construct or fetch
            
            # Fetch permalink
            try:
                media_url = f"https://graph.facebook.com/v18.0/{media_id}"
                media_res = requests.get(media_url, params={"fields": "permalink", "access_token": access_token})
                if "permalink" in media_res.json():
                    permalink = media_res.json()["permalink"]
            except:
                pass # Fallback to constructed link or just ID

            logger.info(f"Successfully published! Media ID: {media_id}")
            
            # Record history
            record = {
                "id": media_id,
                "account_id": account_id,
                "username": account["username"],
                "video_path": video_url, # Store URL instead of path
                "caption": caption,
                "permalink": permalink,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            self.history.append(record)
            self._save_history()
            
            return record

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            # Record failure
            record = {
                "id": f"FAILED_{int(datetime.now().timestamp())}",
                "account_id": account_id,
                "username": account["username"],
                "video_path": video_url,
                "caption": caption,
                "permalink": "",
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self.history.append(record)
            self._save_history()
            raise e

    def get_history(self):
        """Get upload history"""
        return sorted(self.history, key=lambda x: x["timestamp"], reverse=True)
