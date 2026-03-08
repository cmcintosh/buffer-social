#!/usr/bin/env python3
"""
Buffer Social Media Scheduler - OpenClaw Skill

Cross-platform social media posting via Buffer API v1.
Supports Twitter/X, LinkedIn, Facebook, Instagram.

Reference Implementation: Wembassy social media management
Free tier: 3 accounts, 10 scheduled posts max

Usage:
    from buffer_client import BufferClient
    client = BufferClient()
    profiles = client.list_profiles()
    update = client.create_update("Hello world!", profiles)
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class BufferClient:
    """
    Client for Buffer API v1
    
    Defaults to Wembassy configuration
    Free tier: 3 accounts, 10 scheduled posts
    """
    
    BASE_URL = "https://api.bufferapp.com/1"
    FREE_TIER_LIMIT = 10
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Buffer client
        
        Args:
            access_token: Buffer API access token (default: BUFFER_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv('BUFFER_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError(
                "Buffer access token required. "
                "Get one at https://buffer.com/developers"
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make API request and handle response"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text, "status_code": response.status_code}
        elif response.status_code == 204:
            return {"success": True, "status_code": 204}
        else:
            try:
                error = response.json()
            except:
                error = response.text
            raise BufferAPIException(
                f"Request failed: {response.status_code}",
                status_code=response.status_code,
                response=error
            )
    
    # ========================================================================
    # USER / AUTH
    # ========================================================================
    
    def get_user(self) -> Dict:
        """Get current user info"""
        return self._request('GET', '/user.json')
    
    # ========================================================================
    # PROFILES (Connected Social Accounts)
    # ========================================================================
    
    def list_profiles(self) -> List[Dict]:
        """
        List all connected social profiles
        
        Returns:
            List of profile dicts with keys:
            - id: Profile ID (use in posts)
            - service: twitter, linkedin, facebook, instagram
            - formatted_username: @username or Page Name
            - email: Associated email
            - schedules: Posting schedules
        """
        return self._request('GET', '/profiles.json')
    
    def get_profile(self, profile_id: str) -> Dict:
        """Get specific profile details"""
        return self._request('GET', f'/profiles/{profile_id}.json')
    
    def list_profiles_by_service(self, service: str) -> List[Dict]:
        """
        Filter profiles by service
        
        Args:
            service: twitter, linkedin, facebook, or instagram
        """
        all_profiles = self.list_profiles()
        return [p for p in all_profiles if p.get('service') == service]
    
    def get_profile_id_by_service(self, service: str) -> Optional[str]:
        """Get first profile ID for a service"""
        profiles = self.list_profiles_by_service(service)
        return profiles[0].get('id') if profiles else None
    
    # ========================================================================
    # UPDATES (Posts)
    # ========================================================================
    
    def create_update(
        self,
        text: str,
        profile_ids: Union[str, List[str], List[Dict]],
        scheduled_at: Optional[Union[str, datetime]] = None,
        photo: Optional[str] = None,
        photo_url: Optional[str] = None,
        now: bool = False,
        top: bool = False
    ) -> Dict:
        """
        Schedule a new post
        
        Args:
            text: Post content
            profile_ids: Single ID, list of IDs, or list of profile dicts
            scheduled_at: When to post (ISO string or datetime). Must be 10+ min in future.
            photo: Local file path to image (uploaded as media)
            photo_url: URL to image (Buffer fetches from URL)
            now: If True, post immediately
            top: If True, add to top of queue instead of end
        
        Returns:
            Update object with id, text, due_at, etc.
        """
        # Normalize profile_ids
        if isinstance(profile_ids, dict):
            profile_ids = [profile_ids.get('id')]
        elif isinstance(profile_ids, str):
            profile_ids = [profile_ids]
        elif isinstance(profile_ids, list):
            

        # Extract IDs from profile dicts
        profile_ids = [p.get('id') if isinstance(p, dict) else p for p in profile_ids]

        payload = {
            'text': text,
            'profile_ids': profile_ids,
        }
        
        if photo_url:
            payload['photo'] = photo_url
        elif photo:
            # TODO: Handle file uploads
            raise NotImplementedError("File upload not yet implemented (use photo_url)")
        
        if now:
            payload['now'] = True
        elif top:
            payload['top'] = True
        elif scheduled_at:
            if isinstance(scheduled_at, datetime):
                scheduled_at = scheduled_at.isoformat()
            payload['scheduled_at'] = scheduled_at
        
        return self._request('POST', '/updates/create.json', data=json.dumps(payload))
    
    def list_pending(self, profile_id: Optional[str] = None, count: int = 100) -> List[Dict]:
        """
        List scheduled posts
        
        Args:
            profile_id: Filter by specific profile (None = all)
            count: Max posts to return
        """
        if profile_id:
            return self._request('GET', f'/profiles/{profile_id}/updates/pending.json', params={'count': count})
        else:
            # Get pending for all profiles
            pending = []
            for profile in self.list_profiles():
                profile_pending = self._request(
                    'GET', 
                    f'/profiles/{profile["id"]}/updates/pending.json',
                    params={'count': count}
                )
                pending.extend(profile_pending)
            return pending
    
    def list_sent(self, profile_id: Optional[str] = None, count: int = 100) -> List[Dict]:
        """List already-sent posts"""
        if profile_id:
            return self._request('GET', f'/profiles/{profile_id}/updates/sent.json', params={'count': count})
        else:
            sent = []
            for profile in self.list_profiles():
                profile_sent = self._request(
                    'GET',
                    f'/profiles/{profile["id"]}/updates/sent.json',
                    params={'count': count}
                )
                sent.extend(profile_sent)
            return sent
    
    def get_update(self, update_id: str) -> Dict:
        """Get specific post details"""
        return self._request('GET', f'/updates/{update_id}.json')
    
    def update_update(
        self,
        update_id: str,
        text: Optional[str] = None,
        scheduled_at: Optional[Union[str, datetime]] = None
    ) -> Dict:
        """
        Edit a scheduled post
        
        Note: Can only edit text and scheduled time
        """
        payload = {}
        if text is not None:
            payload['text'] = text
        if scheduled_at is not None:
            if isinstance(scheduled_at, datetime):
                scheduled_at = scheduled_at.isoformat()
            payload['scheduled_at'] = scheduled_at
        
        return self._request('POST', f'/updates/{update_id}/update.json', data=json.dumps(payload))
    
    def delete_update(self, update_id: str) -> Dict:
        """Remove a post from queue"""
        return self._request('POST', f'/updates/{update_id}/destroy.json')
    
    def move_to_top(self, update_id: str) -> Dict:
        """Move post to top of queue"""
        return self._request('POST', f'/updates/{update_id}/move_to_top.json')
    
    def shuffle_updates(self, profile_id: str) -> Dict:
        """Randomize queue order for a profile"""
        return self._request('POST', f'/profiles/{profile_id}/updates/shuffle.json')
    
    # ========================================================================
    # QUEUE MANAGEMENT (Free Tier Helpers)
    # ========================================================================
    
    def get_queue_count(self, profile_id: Optional[str] = None) -> int:
        """Count scheduled posts"""
        pending = self.list_pending(profile_id=profile_id)
        return len(pending)
    
    def has_queue_space(self, profile_id: Optional[str] = None, limit: int = FREE_TIER_LIMIT) -> bool:
        """Check if queue has room for more posts"""
        count = self.get_queue_count(profile_id)
        return count < limit
    
    def get_queue_space(self, profile_id: Optional[str] = None, limit: int = FREE_TIER_LIMIT) -> int:
        """Get number of available queue slots"""
        count = self.get_queue_count(profile_id)
        return max(0, limit - count)
    
    def get_next_send_time(self, profile_ids: Optional[List[str]] = None) -> Optional[str]:
        """Find when the next post will go out"""
        if profile_ids is None:
            profiles = self.list_profiles()
            profile_ids = [p['id'] for p in profiles]
        
        earliest_time = None
        for pid in profile_ids:
            pending = self.list_pending(profile_id=pid, count=1)
            if pending:
                due_at = pending[0].get('due_at')
                if due_at:
                    if earliest_time is None or due_at < earliest_at:
                        earliest_time = due_at
        
        return earliest_time
    
    # ========================================================================
    # SCHEDULING HELPERS
    # ========================================================================
    
    def schedule_single(
        self,
        text: str,
        service: str,
        **kwargs
    ) -> Dict:
        """
        Helper to post to first profile of a specific service
        
        Args:
            text: Post text
            service: twitter, linkedin, facebook, instagram
            **kwargs: Passed to create_update
        """
        profile_id = self.get_profile_id_by_service(service)
        if not profile_id:
            raise ValueError(f"No {service} profile connected")
        return self.create_update(text, [profile_id], **kwargs)
    
    def schedule_multi(
        self,
        text: str,
        services: List[str],
        **kwargs
    ) -> Dict:
        """
        Post to multiple services
        
        Args:
            text: Post text
            services: List of services to post to
            **kwargs: Passed to create_update
        """
        profile_ids = []
        for service in services:
            pid = self.get_profile_id_by_service(service)
            if pid:
                profile_ids.append(pid)
        
        if not profile_ids:
            raise ValueError(f"No profiles found for services: {services}")
        
        return self.create_update(text, profile_ids, **kwargs)


class BufferAPIException(Exception):
    """Buffer API error"""
    def __init__(self, message: str, status_code: int = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


# ============================================================================
# CLI INTERFACE
# ============================================================================

def cli_main():
    parser = argparse.ArgumentParser(description='Buffer Social Media Scheduler CLI')
    subparsers = parser.add_subparsers(dest='command')
    
    # List profiles
    subparsers.add_parser('list-profiles', help='List connected social accounts')
    
    # Create update
    create = subparsers.add_parser('create-update', help='Schedule a post')
    create.add_argument('--text', '-t', required=True, help='Post text')
    create.add_argument('--profiles', '-p', help='Profile IDs (comma-separated)')
    create.add_argument('--service', '-s', help='Service name (twitter, linkedin, facebook, instagram)')
    create.add_argument('--photo-url', help='Image URL')
    create.add_argument('--now', action='store_true', help='Post immediately')
    
    # List pending
    subparsers.add_parser('list-pending', help='List scheduled posts')
    
    # List sent
    subparsers.add_parser('list-sent', help='List sent posts')
    
    # Queue status
    subparsers.add_parser('queue-status', help='Check queue space')
    
    # Delete
    delete = subparsers.add_parser('delete-update', help='Remove from queue')
    delete.add_argument('--id', required=True, help='Update ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        client = BufferClient()
        
        if args.command == 'list-profiles':
            profiles = client.list_profiles()
            print(f"Connected profiles: {len(profiles)}")
            for p in profiles:
                print(f"  {p['service']}: {p['formatted_username']} (ID: {p['id']})")
        
        elif args.command == 'create-update':
            if args.service:
                result = client.schedule_single(args.text, args.service, photo_url=args.photo_url, now=args.now)
            elif args.profiles:
                profile_ids = args.profiles.split(',')
                result = client.create_update(args.text, profile_ids, photo_url=args.photo_url, now=args.now)
            else:
                # Post to all
                profiles = client.list_profiles()
                result = client.create_update(args.text, profiles, photo_url=args.photo_url, now=args.now)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'list-pending':
            pending = client.list_pending()
            print(f"Scheduled posts: {len(pending)}")
            for p in pending:
                print(f"  {p.get('due_at', 'ASAP')}: {p['text'][:60]}...")
        
        elif args.command == 'list-sent':
            sent = client.list_sent()
            print(f"Sent posts: {len(sent)}")
            for s in sent:
                print(f"  {s.get('sent_at', 'Unknown')}: {s['text'][:60]}...")
        
        elif args.command == 'queue-status':
            count = client.get_queue_count()
            space = client.get_queue_space()
            print(f"Queue: {count}/10 (Free tier limit)")
            print(f"Available slots: {space}")
            print(f"Has space: {client.has_queue_space()}")
        
        elif args.command == 'delete-update':
            result = client.delete_update(args.id)
            print(f"Deleted: {result}")
        
    except BufferAPIException as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response:
            print(f"Response: {e.response}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Check if running as CLI
    if len(sys.argv) > 1:
        cli_main()
    else:
        # Show help or run tests
        print("Buffer Social Media Scheduler")
        print("Run: python buffer_client.py --help")
