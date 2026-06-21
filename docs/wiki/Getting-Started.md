# Getting Started

## Your First Post

Let's create your first social media post using Buffer Social.

### Step 1: Import the Client

```python
from scripts.buffer_client import BufferClient

# Initialize client (reads BUFFER_ACCESS_TOKEN from .env)
client = BufferClient()
```

### Step 2: Get Organization and Channels

```python
# Get your default organization
org_id = client.get_default_organization_id()

# Get all connected channels
channels = client.get_channels(org_id)

# Find specific channel by service
twitter_id = client.get_first_channel_id(org_id, service="twitter")
print(f"Twitter channel ID: {twitter_id}")
```

### Step 3: Post Immediately

The simplest way to post:

```python
# Post to specific service
result = client.post_now("Hello from Buffer Social! 🚀", service="twitter")
print(f"Posted successfully: {result}")
```

This will:
1. Find your Twitter channel automatically
2. Post immediately using `shareNow` mode
3. Return the post details

### Step 4: Post with More Control

For full control over the posting process:

```python
# Get channel ID
channel_id = client.get_first_channel_id(org_id, service="twitter")

# Create post with specific mode
result = client.create_post(
    channel_id=channel_id,
    text="Hello with full control! 🎉",
    mode="shareNow",  # Post immediately
    scheduling_type="automatic"
)

print(f"Post ID: {result['post']['id']}")
print(f"Status: {result['post']['status']}")
```

## Scheduling Posts

### Schedule for Later

```python
from datetime import datetime, timedelta

# Schedule for tomorrow at 9 AM
schedule_time = datetime.now() + timedelta(days=1)
schedule_time = schedule_time.replace(hour=9, minute=0, second=0)

result = client.schedule_post(
    text="Scheduled post for tomorrow! 📅",
    due_at=schedule_time,
    service="twitter"
)
```

### Time Format

The `due_at` parameter accepts:
- Python `datetime` objects
- ISO8601 strings (e.g., `"2026-06-22T09:00:00Z"`)

Always use UTC timezone for consistency.

## Posting with Images

### Post with Image URL

```python
result = client.create_image_post(
    channel_id=twitter_id,
    text="Check out this image! 🖼️",
    image_url="https://yoursite.com/images/photo.jpg",
    mode="shareNow"
)
```

**Requirements:**
- Image URL must be publicly accessible
- Use HTTPS URLs
- Supported formats: JPG, PNG, GIF

## Multi-Platform Posting

Post the same content to multiple platforms:

```python
content = "Big news! 🎉 We're launching soon."
services = ['twitter', 'facebook', 'googlebusiness']

for service in services:
    try:
        result = client.post_now(content, service=service)
        print(f"✅ Posted to {service}")
    except Exception as e:
        print(f"❌ Failed on {service}: {e}")
```

## Local Scheduling Strategy

Instead of relying on Buffer's queue, keep your calendar local:

```python
# Your content calendar (JSON, database, etc.)
content_calendar = [
    {
        "datetime": "2026-06-22T09:00:00Z",
        "text": "Morning post! ☕",
        "services": ["twitter"]
    },
    {
        "datetime": "2026-06-22T17:00:00Z",
        "text": "Evening post! 🌅",
        "services": ["twitter", "facebook"]
    }
]

# When your scheduler runs:
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
for post in content_calendar:
    post_time = datetime.fromisoformat(post["datetime"].replace('Z', '+00:00'))
    
    # Check if it's time to publish
    if post_time <= now < post_time + timedelta(minutes=5):
        for service in post["services"]:
            client.post_now(post["text"], service=service)
```

## CLI Quick Start

You can also use the command line:

```bash
# List channels
python scripts/buffer_client.py channels

# Post immediately
python scripts/buffer_client.py \
  post \
  --text "Hello from CLI! 🚀" \
  --services twitter

# List recent posts
python scripts/buffer_client.py posts --limit 5
```

## Next Steps

- [[API Reference]] - Explore all available methods
- [[Troubleshooting]] - Common issues and solutions
- [[Security]] - Best practices for production use
