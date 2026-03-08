# Buffer Social Media Scheduler Skill

Cross-platform social media posting via Buffer GraphQL API v2.

> **Note:** This skill was built for **Wembassy** social media management using Buffer's GraphQL API (`api.buffer.com/graphql`). Uses Buffer's free tier (10 scheduled post limit).

## Quick Start Flow

**3-Step Flow:** Org → Channel → Post

```python
from buffer_client import BufferClient

client = BufferClient()

# Step 1: Get Organization
org_id = client.get_default_organization_id()
print(f"Org: {org_id}")

# Step 2: Get Channels (connected accounts)
channels = client.get_channels(org_id)
for ch in channels:
    print(f"  {ch['service']}: {ch['name']}")

# Step 3: Post to a channel
post = client.add_to_queue(
    text="Hello world! 🚀",
    service="twitter"  # or "facebook", "googlebusiness"
)
post_id = post['id']
print(f"Posted: {post_id}")
```

## Setup

### 1. Create Buffer Account
- Sign up at https://buffer.com
- Connect social accounts (Twitter/X, LinkedIn, Facebook, Google Business)

### 2. Get API Access Token
- Go to https://buffer.com/developers
- Create an app → Get Access Token

### 3. Configure Skill
```bash
cp .env.example .env
# Edit .env with your token
```

## Configuration

| Variable | Description |
|----------|-------------|
| `BUFFER_ACCESS_TOKEN` | Buffer API access token |

## Limits

| Resource | Free Tier |
|----------|-----------|
| Scheduled posts | 10 maximum |
| Social accounts | 3 |

## Usage

### Initialize Client
```python
from buffer_client import BufferClient

client = BufferClient()
```

### List Connected Channels
```python
org_id = client.get_default_organization_id()
channels = client.get_channels(org_id)

for ch in channels:
    print(f"{ch['service']}: {ch['name']}")
```

### Schedule a Post
```python
# Add to queue (posts at next available slot)
client.add_to_queue(
    text="Hello from Wembassy! 🚀",
    service="twitter"  # or "facebook" etc.
)

# Post immediately
client.post_now(
    text="Live now!",
    service="twitter"
)

# Schedule for specific time
from datetime import datetime, timedelta

due_at = (datetime.now() + timedelta(days=1)).isoformat()
client.schedule_post(
    text="Tomorrow's post",
    due_at=due_at,
    service="twitter"
)

# Post with image
client.create_image_post(
    channel_id=channel_id,
    text="Check out this image! 🖼️",
    image_url="https://example.com/image.jpg",
    mode="addToQueue"
)
```

### List and Read Posts
```python
# Get all posts
posts = client.get_posts(org_id, limit=10)
for edge in posts['edges']:
    post = edge['node']
    print(f"[{post['status']}] {post['text'][:50]}")

# Get specific post
details = client.get_post(POST_ID)
print(f"Text: {details['text']}")
```

## API Methods

### Account
- `get_account()` - Get account info with organizations

### Organizations
- `get_organizations()` - List user's organizations
- `get_default_organization_id()` - Get first org (convenience)

### Channels
- `get_channels(organization_id)` - List connected channels
- `get_channel(channel_id)` - Get channel details
- `get_first_channel_id(organization_id, service)` - Get channel by service

### Posts (CRUD)
- `create_post(channel_id, text, mode, ...)` - Create new post
  - `mode`: `addToQueue`, `shareNow`, `customScheduled`, `shareNext`, `recommendedTime`
  - `scheduling_type`: `automatic` or `notification`
- `get_post(post_id)` - Get post details
- `get_posts(organization_id, limit)` - List posts

### Helper Methods
- `post_now(text, service)` - Post immediately
- `add_to_queue(text, service)` - Add to end of queue
- `schedule_post(text, due_at, service)` - Schedule for specific time

## CLI Usage

```bash
# List connected channels
python scripts/buffer_client.py channels

# Create a post
python scripts/buffer_client.py post \
  --text "Hello from Wembassy!" \
  --services twitter

# List recent posts
python scripts/buffer_client.py posts --limit 5
```

## Integration Tips

**Keep queue full (9-10 posts):**
```python
# Check if we need more posts
org_id = client.get_default_organization_id()
posts = client.get_posts(org_id, limit=10)
if len(posts['edges']) < 10:
    # Add new post from content calendar
    client.add_to_queue(text="Next post...")
```

## Connected Accounts (Wembassy)

| Service | Account | Channel ID |
|---------|---------|------------|
| Twitter | @TeamWembassy | [TWITTER_CHANNEL_ID] |
| Facebook | Wembassy - Drupal, Wordpress... | [ID from list] |
| Google Business | Wembassy LLC | [ID from list] |

## Requirements

- Python 3.7+
- `requests`
- `python-dotenv`

## Troubleshooting

**400 Bad Request**: Check query syntax - use GraphQL introspection
**401 Unauthorized**: Token expired - regenerate
**No channels found**: Check organization ID

## API Reference

**Buffer GraphQL v2**
- Base URL: `https://api.buffer.com/graphql`
- Auth: Bearer token
- Docs: https://developers.buffer.com/reference.html

## License

Internal use for Wembassy operations.
