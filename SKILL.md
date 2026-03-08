# Buffer Social Media Scheduler Skill

Cross-platform social media publishing via Buffer GraphQL API v2.

> **Strategy:** Keep scheduling **LOCAL** - only push to Buffer when ready to publish. This gives us full control over timing and content calendar.

## Connected Accounts (Wembassy)

| Service | Account | Channel ID |
|---------|---------|------------|
| **Twitter/X** | @TeamWembassy | `[TWITTER_CHANNEL_ID]` |
| **Facebook** | Wembassy - Drupal, Wordpress, Website Development | `[FACEBOOK_CHANNEL_ID]` |
| **Google Business** | Wembassy LLC | `[GOOGLE_CHANNEL_ID]` |

## Setup

### 1. Buffer Account
- Already configured with cmcintosh@wembassy.com
- 3 social accounts connected (max for free tier)
- 10 scheduled post limit in Buffer queue

### 2. Configure Skill
```bash
cp .env.example .env
# Edit .env with your token
```

## Configuration

| Variable | Description |
|----------|-------------|
| `BUFFER_ACCESS_TOKEN` | Buffer API access token |

## Usage

### Publishing Flow (Local Scheduling)

**Recommended:** Keep your content calendar local, push to Buffer only when ready:

```python
from buffer_client import BufferClient

client = BufferClient()

# Get your channels
org_id = client.get_default_organization_id()
channels = client.get_channels(org_id)

# Find specific channels
twitter_id = [c['id'] for c in channels if c['service'] == 'twitter'][0]
facebook_id = [c['id'] for c in channels if c['service'] == 'facebook'][0]
google_id = [c['id'] for c in channels if c['service'] == 'googlebusiness'][0]

# POST IMMEDIATELY (Recommended for local scheduling)
# When your local scheduler says "publish now":
result = client.post_now("Content goes live! 🚀", service="twitter")
# result = client.post_now("Same content", service="facebook")

# SCHEDULE FOR SPECIFIC TIME (Use your own calendar, not Buffer's queue)
from datetime import datetime, timezone
due_at = "2026-03-15T14:00:00Z"  # ISO8601 UTC
client.schedule_post(
    text="Scheduled via our system",
    due_at=due_at,
    service="twitter"
)

# POST WITH IMAGE
client.create_image_post(
    channel_id=twitter_id,
    text="Post with image! 🖼️",
    image_url="https://wembassy.com/images/post.jpg"
)

# POST TO MULTIPLE PLATFORMS
for service in ['twitter', 'facebook', 'googlebusiness']:
    client.post_now(f"Multi-platform post! 🚀", service=service)
```

### Manual Flow (Full Control)

```python
client = BufferClient()

# Step 1: Get Organization
org_id = client.get_default_organization_id()

# Step 2: Get Channels
channels = client.get_channels(org_id)
twitter_id = [c['id'] for c in channels if c['service'] == 'twitter'][0]

# Step 3: Post immediately (no Buffer queue)
client.create_post(
    channel_id=twitter_id,
    text="Direct post bypassing queue!",
    mode="shareNow"  # Post immediately, no queue
)
```

## Publishing Modes

| Mode | Use Case |
|------|----------|
| `shareNow` | ✅ **Post immediately** (recommended) |
| `customScheduled` | Schedule for specific time (use local calendar) |
| `addToQueue` | Add to Buffer queue (not recommended - prefer local) |

## API Methods

### Organizations
- `get_default_organization_id()` - Get Wembassy org ID

### Channels
- `get_channels(organization_id)` - List connected accounts
- `get_first_channel_id(organization_id, service)` - Get by service

### Publishing (Primary Methods)
- `post_now(text, service)` - ✅ **Publish immediately**
- `schedule_post(text, due_at, service)` - Schedule with local datetime
- `create_image_post(...)` - Post with image attachment

### Low-Level
- `create_post(channel_id, text, mode, ...)` - Full control over mode

## Local Scheduling Strategy

**Don't rely on Buffer's 10-post queue.** Use your own system:

```python
# Your content calendar (local)
posts_scheduled = [
    {"time": "2026-03-10T09:00:00Z", "text": "Morning post! ☕", "services": ["twitter", "facebook"]},
    {"time": "2026-03-10T17:00:00Z", "text": "Evening post! 🌅", "services": ["twitter"]},
]

# When cron/scheduler fires:
for post in posts_ready_to_publish:
    for service in post['services']:
        client.post_now(post['text'], service=service)
```

## CLI Usage

```bash
# List connected accounts
python scripts/buffer_client.py channels

# Post immediately
python scripts/buffer_client.py \
  post \
  --text "Live now! 🚀" \
  --services twitter

# List recent posts
python scripts/buffer_client.py posts --limit 5
```

## Limits

| Resource | Value |
|----------|-------|
| Connected accounts | 3 (Twitter, Facebook, Google Business) |
| Buffer queue size | 10 max |
| **Recommended approach** | Keep calendar local, push on demand |

## Requirements

- Python 3.7+
- `requests`, `python-dotenv`

## API Reference

**Buffer GraphQL v2**
- Base: `https://api.buffer.com/graphql`
- Auth: Bearer token
- Docs: https://developers.buffer.com/reference.html

## Important Notes

### Deletion
**Buffer GraphQL API does NOT support deleting posts.** You must delete manually from the Buffer dashboard:
1. Go to https://buffer.com
2. Navigate to the account's queue
3. Click the X/Delete on posts

### Test Posts
Be careful when testing - posts go live immediately with `shareNow`! Always clean up test posts from the Buffer dashboard.

## License

Internal use for Wembassy operations.
