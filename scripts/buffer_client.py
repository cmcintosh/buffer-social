#!/usr/bin/env python3
"""
Buffer Social Media Scheduler - OpenClaw Skill
GraphQL API v2 for Buffer

Cross-platform social media posting via Buffer API v2 (GraphQL).
Supports Twitter/X, LinkedIn, Facebook, Instagram.

Reference Implementation: Wembassy social media management
Free tier: 3 channels, limited posts

Usage:
    from buffer_client import BufferClient
    client = BufferClient()
    channels = client.get_channels()
    post = client.create_post(text="Hello!", channel_ids=['xxx'])
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from pathlib import Path

import requests

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
    Client for Buffer GraphQL API v2
    
    Base URL: https://graph.buffer.com
    Auth: Bearer token in Authorization header
    """
    
    BASE_URL = "https://api.buffer.com"
    FREE_TIER_LIMIT = 10
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Buffer GraphQL client
        
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
        })
    
    def _graphql(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Execute GraphQL query/mutation
        
        Args:
            query: GraphQL query string
            variables: Variables dict for the query
            
        Returns:
            Response data (under 'data' key) or raises exception
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/graphql",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise BufferAPIException(
                f"HTTP Error: {response.status_code}",
                status_code=response.status_code,
                response=response.text
            )
        
        data = response.json()
        
        if 'errors' in data:
            errors = data['errors']
            error_msg = '; '.join([e.get('message', 'Unknown error') for e in errors])
            raise BufferAPIException(
                f"GraphQL Error: {error_msg}",
                response=errors
            )
        
        return data.get('data', {})
    
    # ========================================================================
    # ACCOUNT / USER
    # ========================================================================
    
    def get_account(self) -> Dict:
        """
        Get authenticated user's account information including organizations
        
        Returns:
            User account details with organizations
        """
        query = """
        query {
          account {
            id
            email
            name
            organizations {
              id
              name
            }
          }
        }
        """
        result = self._graphql(query)
        return result.get('account', {})
    
    # ========================================================================
    # CHANNELS (Connected Social Accounts)
    # ========================================================================
    
    def get_channels(self, organization_id: str) -> List[Dict]:
        """
        Get all connected channels (social accounts) for an organization
        
        Args:
            organization_id: The organization ID (from account.organizations)
            
        Returns:
            List of channel objects with id, name, service, etc.
        """
        query = """
        query {
          channels(input: { organizationId: "%s" }) {
            id
            name
            service
          }
        }
        """ % organization_id
        result = self._graphql(query)
        return result.get('channels', [])
    
    def get_channel(self, channel_id: str) -> Dict:
        """Get specific channel by ID"""
        query = """
        query GetChannel($input: ChannelInput!) {
          channel(input: $input) {
            id
            name
            service
          }
        }
        """
        result = self._graphql(query, {'input': {'id': channel_id}})
        return result.get('channel', {})
    
    def get_channels_by_service(self, organization_id: str, service: str) -> List[Dict]:
        """
        Filter channels by service type
        
        Args:
            organization_id: The organization ID
            service: 'twitter', 'linkedin', 'facebook', 'instagram', etc.
        """
        all_channels = self.get_channels(organization_id)
        return [c for c in all_channels if c.get('service') == service]
    
    def get_first_channel_id(self, organization_id: str, service: Optional[str] = None) -> Optional[str]:
        """Get first channel ID optionally filtered by service"""
        channels = self.get_channels(organization_id)
        if service:
            channels = [c for c in channels if c.get('service') == service]
        return channels[0].get('id') if channels else None
    
    def get_organizations(self) -> List[Dict]:
        """Get user's organizations"""
        query = """
        query {
          account {
            organizations {
              id
              name
            }
          }
        }
        """
        result = self._graphql(query)
        account = result.get('account', {})
        return account.get('organizations', [])
    
    # ========================================================================
    # POSTS
    # ========================================================================
    
    def create_post(
        self,
        channel_id: str,
        text: str,
        scheduling_type: str = "automatic",
        mode: str = "addToQueue",
        due_at: Optional[str] = None,
        assets: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new post
        
        Args:
            channel_id: Channel ID to post to (single channel)
            text: Post content
            scheduling_type: "automatic" or "notification"
            mode: "addToQueue", "shareNow", "shareNext", "customScheduled", "recommendedTime"
            due_at: ISO8601 datetime string for custom scheduling (mode=customScheduled)
            assets: List of media assets
            metadata: Additional post metadata
            
        Returns:
            Created post object
        """
        input_data = {
            'channelId': channel_id,
            'schedulingType': scheduling_type,
            'mode': mode,
            'text': text
        }
        
        if due_at and mode == "customScheduled":
            input_data['dueAt'] = due_at
        
        if assets:
            input_data['assets'] = assets
        
        if metadata:
            input_data['metadata'] = metadata
        
        query = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post {
                id
                text
                status
                channel {
                  id
                  name
                  service
                }
              }
            }
          }
        }
        """
        
        result = self._graphql(query, {'input': input_data})
        return result.get('createPost', {})
    
    def get_posts(
        self,
        organization_id: str,
        limit: int = 10,
        cursor: Optional[str] = None
    ) -> Dict:
        """
        Get posts for the organization
        
        Args:
            organization_id: Organization ID
            limit: Number of posts to return
            cursor: Cursor for pagination
            
        Returns:
            Posts list with pagination info
        """
        variables = {
            'input': {
                'organizationId': organization_id
            }
        }
        
        if cursor:
            variables['input']['after'] = cursor
        
        query = """
        query GetPosts($input: PostsInput!) {
          posts(input: $input) {
            edges {
              node {
                id
                text
                status
                dueAt
                sentAt
                createdAt
                updatedAt
                channel {
                  id
                  name
                  service
                }
              }
              cursor
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """
        
        result = self._graphql(query, variables)
        return result.get('posts', {})
    
    def get_post(self, post_id: str) -> Dict:
        """Get specific post by ID"""
        query = """
        query GetPost($input: PostInput!) {
          post(input: $input) {
            id
            text
            status
            dueAt
            sentAt
            createdAt
            updatedAt
            channel {
              id
              name
              service
            }
          }
        }
        """
        result = self._graphql(query, {'input': {'id': post_id}})
        return result.get('post', {})
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete/unschedule a post"""
        # The mutation might be different - let's try
        query = """
        mutation DeletePost($input: DeletePostInput!) {
          deletePost(input: $input) {
            ... on PostActionSuccess {
              success
              post {
                id
              }
            }
          }
        }
        """
        return self._graphql(query, {'input': {'id': post_id}})
    
    # ========================================================================
    # SIMPLIFIED HELPERS
    # ========================================================================
    
    def get_default_organization_id(self) -> str:
        """Get the first organization ID (convenience method)"""
        orgs = self.get_organizations()
        if not orgs:
            raise ValueError("No organizations found")
        return orgs[0]['id']
    
    def post_now(self, text: str, service: Optional[str] = None) -> Dict:
        """
        Post immediately to specified service
        
        Args:
            text: Post content
            service: Service name (twitter, facebook, etc.) or None for first available
        """
        org_id = self.get_default_organization_id()
        
        if service:
            channel_id = self.get_first_channel_id(org_id, service)
        else:
            channel_id = self.get_first_channel_id(org_id)
        
        if not channel_id:
            raise ValueError("No active channels found")
        
        return self.create_post(channel_id, text, mode="shareNow")
    
    def schedule_post(
        self,
        text: str,
        due_at: str,
        service: Optional[str] = None
    ) -> Dict:
        """
        Schedule a post for a specific time
        
        Args:
            text: Post content
            due_at: ISO8601 datetime string
            service: Service name (twitter, facebook, etc.)
        """
        org_id = self.get_default_organization_id()
        
        if service:
            channel_id = self.get_first_channel_id(org_id, service)
        else:
            channel_id = self.get_first_channel_id(org_id)
        
        if not channel_id:
            raise ValueError("No active channels found")
        
        return self.create_post(channel_id, text, mode="customScheduled", due_at=due_at)
    
    def add_to_queue(self, text: str, service: Optional[str] = None) -> Dict:
        """
        Add post to queue (end of queue)
        
        Args:
            text: Post content
            service: Service name
        """
        org_id = self.get_default_organization_id()
        
        if service:
            channel_id = self.get_first_channel_id(org_id, service)
        else:
            channel_id = self.get_first_channel_id(org_id)
        
        if not channel_id:
            raise ValueError("No active channels found")
        
        return self.create_post(channel_id, text, mode="addToQueue")


class BufferAPIException(Exception):
    """Buffer GraphQL API error"""
    def __init__(self, message: str, status_code: int = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


# ============================================================================
# CLI INTERFACE
# ============================================================================

def cli_main():
    parser = argparse.ArgumentParser(description='Buffer Social Media Scheduler CLI (GraphQL API)')
    subparsers = parser.add_subparsers(dest='command')
    
    # Account info
    subparsers.add_parser('account', help='Get account info')
    
    # List channels
    subparsers.add_parser('channels', help='List connected channels')
    
    # Create post
    post_parser = subparsers.add_parser('post', help='Create a post')
    post_parser.add_argument('--text', '-t', required=True, help='Post text')
    post_parser.add_argument('--services', '-s', help='Services (comma-separated: twitter,linkedin)')
    post_parser.add_argument('--schedule', help='Schedule ISO datetime (or "now")')
    
    # List posts
    posts_parser = subparsers.add_parser('posts', help='List posts')
    posts_parser.add_argument('--limit', '-l', type=int, default=10, help='Number of posts')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        client = BufferClient()
        
        if args.command == 'account':
            account = client.get_account()
            print(json.dumps(account, indent=2))
        
        elif args.command == 'channels':
            org_id = client.get_default_organization_id()
            channels = client.get_channels(org_id)
            print(f"Connected channels: {len(channels)}")
            for ch in channels:
                print(f"  ✓ {ch['service']}: {ch['name']} ({ch['id'][:8]}...)")
        
        elif args.command == 'post':
            if args.schedule and args.schedule != 'now':
                service = args.services.split(',')[0] if args.services else None
                result = client.schedule_post(args.text, args.schedule, service)
            else:
                service = args.services.split(',')[0] if args.services else None
                result = client.post_now(args.text, service)
            
            print(json.dumps(result, indent=2))
        
        elif args.command == 'posts':
            org_id = client.get_default_organization_id()
            posts = client.get_posts(org_id, limit=args.limit)
            edges = posts.get('edges', [])
            print(f"Found {len(edges)} posts:")
            for edge in edges:
                node = edge.get('node', {})
                print(f"  [{node.get('status')}] {node.get('text', '')[:50]}...")
        
    except BufferAPIException as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.response:
            print(f"Response: {e.response}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli_main()
