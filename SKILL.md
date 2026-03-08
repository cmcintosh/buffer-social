# Buffer Social Media Scheduler Skill

Cross-platform social media posting via Buffer GraphQL API v2. Manage Twitter/X, LinkedIn, Facebook, and Instagram from one interface.

> **Note:** This skill was built for **Wembassy** social media management using Buffer's GraphQL API (`api.buffer.com/graphql`). Uses Buffer's free tier (10 scheduled post limit).

## Setup

### 1. Create Buffer Account
- Sign up at https://buffer.com
- Connect social accounts (Twitter/X, LinkedIn, Facebook, Instagram)
- Upgrade not required for free tier

### 2. Get API Access Token
- Go to https://buffer.com/developers
- Create a new app
- Get your **Access Token**

### 3. Configure Skill
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `BUFFER_ACCESS_TOKEN` | Buffer API access token | ✅ |
| `BUFFER_DEFAULT_PROFILES` | Default profile IDs (comma-separated) | Optional |

## Buffer Free Tier Limits

| Limit | Value |
|-------|-------|
| Scheduled posts | **10 maximum** |
| Social accounts | 3 |
| Profiles per post | 1-4 |
| Image attachments | ✅ Supported |
| Video attachments | ❌ Not on free tier |

## API Methods

### Profiles (Connected Accounts)
- `list_profiles()` - Get all connected social accounts
- `get_profile(profile_id)` - Get specific profile details

### Updates (Posts)
- `list_pending()` - Get scheduled posts (up to 10)
- `list_sent()` - Get posted history
- `create_update(text, profile_ids, ...)` - Schedule new post
- `get_update(update_id)` - Get post details
- `update_update(update_id, text, ...)` - Edit scheduled post
- `delete_update(update_id)` - Remove from queue
- `shuffle_updates(profile_id)` - Randomize queue order

### Queue Management
- `get_queue_count(profile_id=None)` - Count scheduled posts
- `has_queue_space(profile_id=None)` - Check if queue has room
- `get_next_send_time(profile_ids)` - When will next post go out

## Usage Examples

### Initialize Client
```python
from buffer_client import BufferClient

client = BufferClient()
```

### List Connected Accounts
```python
profiles = client.list_profiles()
for profile in profiles:
    print(f"{profile['service']}: {profile['formatted_username']}")
    # twitter: @wembassy
    # linkedin: Wembassy
```

### Schedule a Post
```python
# Post to all profiles
update = client.create_update(
    text="Check out our latest blog post! 🚀 https://wembassy.com/blog",
    profile_ids=profiles  # Post to all connected accounts
)
print(f"Scheduled: {update['id']}")
print(f"Will post at: {update['due_at']}")
```

### Schedule with Image
```python
update = client.create_update(
    text="New automation service launch!",
    profile_ids=[twitter_id, linkedin_id],  # Specific platforms only
    photo_url="https://wembassy.com/images/launch.png"
)
```

### List Scheduled Posts
```python
pending = client.list_pending()
print(f"You have {len(pending)} posts in queue")
for post in pending:
    print(f"  {post['due_at']}: {post['text'][:50]}...")
```

### Check Queue Space
```python
if client.has_queue_space():
    # Add another post to maintain 9-10 posts in queue
    client.create_update(text="Scheduled post", ...)
else:
    print("Queue full - wait for a post to go out")
```

### Update Scheduled Post
```python
client.update_update(
    update_id="123456789",
    text="Updated text for the post"
)
```

### Delete from Queue
```python
client.delete_update("123456789")
```

## CLI Usage

```bash
# List connected accounts
python scripts/buffer_client.py list-profiles

# Schedule a text post
python scripts/buffer_client.py create-update \
  --text "Hello from Wembassy!" \
  --profiles "profile-id-1,profile-id-2"

# List scheduled posts
python scripts/buffer_client.py list-pending

# Check queue space
python scripts/buffer_client.py queue-status

# Delete a scheduled post
python scripts/buffer_client.py delete-update --id 123456789
```

## Integration with Existing LinkedIn Scheduler

**Strategy: Use Buffer queue as 10-slot "staging area"**

```python
# Daily check (via heartbeat)
if buffer_client.has_queue_space():
    # Pull next post from our internal queue
    next_post = linkedin_scheduler.get_next_post()
    
    # Add to Buffer (publishes to LinkedIn + Twitter/X)
    buffer_client.create_update(
        text=next_post['text'],
        profile_ids=['twitter_profile_id', 'linkedin_profile_id'],
        scheduled_at=next_post['publish_time']
    )
```

## Multi-Platform Posting Strategy

| Platform | Strategy |
|----------|----------|
| **LinkedIn** | Long-form content, industry insights |
| **Twitter/X** | Shorter updates, quick tips |
| **Facebook** | Community engagement |
| **Instagram** | Visual content, behind-scenes |

**Example: Blog announcement**
```python
text_linkedin = """New blog post: The Wembassy Method for Automation

We break down our 4-step process for implementing business automation...

Read more: https://wembassy.com/blog/the-wembassy-method"""

text_twitter = "We just published our automation methodology 🚀 Check it out: https://wembassy.com/blog/the-wembassy-method"

# Schedule separately for platform optimization
buffer_client.create_update(text=text_linkedin, profile_ids=[linkedin_id])
buffer_client.create_update(text=text_twitter, profile_ids=[twitter_id])
```

## Requirements

- Python 3.7+
- `requests` library

## API Reference

**Buffer API v1**
- Base URL: `https://api.bufferapp.com/1`
- Auth: OAuth 2.0 Bearer token in header
- Rate limits: 60 requests/minute (buffered)

## Troubleshooting

**400 "Unsupported Content-Type"**:
- API endpoint changed - try `api.buffer.com/4/` or `publish.buffer.com/1/`
- Token format may have changed - regenerate at buffer.com/developers

**401 Unauthorized**:
- Access token expired - regenerate at buffer.com/developers
- Token may be for different API version

**403 Forbidden**:
- Free tier limit reached (10 scheduled posts)
- Connected account limit reached (3 accounts)

**500 Server Error**:
- Buffer API may be temporarily down
- Try again in a few minutes

**Profile not found**:
- Check profile ID with `list_profiles()`
- Ensure account is connected in Buffer dashboard

**Image upload failed**:
- Use direct image URLs (Buffer fetches from URL)
- Max image size: 8MB (free tier)

## Important Notes

- Posts must be scheduled **at least 10 minutes** in the future
- Free tier: 3 social accounts, 10 scheduled posts
- Video posting requires paid Buffer plan
- Instagram requires mobile confirmation for some posts

## License

Internal use for Wembassy social media operations.
