# API Reference

## BufferClient Class

The main interface for interacting with the Buffer API.

### Initialization

```python
from scripts.buffer_client import BufferClient

# Read token from environment
client = BufferClient()

# Or provide token explicitly
client = BufferClient(access_token="your_token_here")
```

**Raises:**
- `ValueError` if no access token provided and `BUFFER_ACCESS_TOKEN` env var not set

---

## Account Management

### get_account()

Get authenticated user's account information.

```python
account = client.get_account()
print(account['email'])
print(account['name'])
print(account['organizations'])
```

**Returns:** `Dict` with keys:
- `id`: Account ID
- `email`: User email
- `name`: User name
- `organizations`: List of organizations

### get_organizations()

Get all organizations the user has access to.

```python
orgs = client.get_organizations()
for org in orgs:
    print(f"{org['name']}: {org['id']}")
```

**Returns:** `List[Dict]` - Organization objects with `id` and `name`

### get_default_organization_id()

Get the first organization's ID (convenience method).

```python
org_id = client.get_default_organization_id()
```

**Returns:** `str` - Organization ID

**Raises:**
- `ValueError` if no organizations found

---

## Channel Management

### get_channels(organization_id)

Get all connected channels (social accounts).

```python
channels = client.get_channels(org_id)
for channel in channels:
    print(f"{channel['service']}: {channel['id']}")
```

**Parameters:**
- `organization_id` (str): Organization ID

**Returns:** `List[Dict]` - Channel objects with:
- `id`: Channel ID
- `name`: Channel name
- `service`: Service type (twitter, facebook, etc.)

### get_channel(channel_id)

Get specific channel by ID.

```python
channel = client.get_channel("channel_id_here")
```

**Parameters:**
- `channel_id` (str): Channel ID

**Returns:** `Dict` - Channel details

### get_channels_by_service(organization_id, service)

Filter channels by service type.

```python
twitter_channels = client.get_channels_by_service(org_id, "twitter")
```

**Parameters:**
- `organization_id` (str): Organization ID
- `service` (str): Service name (twitter, facebook, linkedin, etc.)

**Returns:** `List[Dict]` - Matching channels

### get_first_channel_id(organization_id, service=None)

Get first channel ID, optionally filtered by service.

```python
# Get first channel of any service
channel_id = client.get_first_channel_id(org_id)

# Get first Twitter channel
twitter_id = client.get_first_channel_id(org_id, service="twitter")
```

**Parameters:**
- `organization_id` (str): Organization ID
- `service` (str, optional): Filter by service

**Returns:** `str` or `None` - Channel ID if found

---

## Publishing

### create_post()

Create a post with full control.

```python
result = client.create_post(
    channel_id="channel_id",
    text="Hello World!",
    mode="shareNow",
    scheduling_type="automatic"
)
```

**Parameters:**
- `channel_id` (str): Channel to post to
- `text` (str): Post content
- `scheduling_type` (str): `"automatic"` or `"notification"`
- `mode` (str): `"addToQueue"`, `"shareNow"`, `"shareNext"`, `"customScheduled"`, `"recommendedTime"`
- `due_at` (str, optional): ISO8601 datetime for custom scheduling
- `assets` (List[Dict], optional): Media attachments
- `metadata` (Dict, optional): Additional metadata

**Returns:** `Dict` - Created post object

### post_now()

Quick post immediately (convenience method).

```python
result = client.post_now("Hello! 🚀", service="twitter")
```

**Parameters:**
- `text` (str): Post content
- `service` (str, optional): Service name (twitter, facebook, etc.)

**Returns:** `Dict` - Created post object

**Raises:**
- `ValueError` if no channels found

### schedule_post()

Schedule a post for a specific time.

```python
from datetime import datetime

result = client.schedule_post(
    text="Scheduled post! 📅",
    due_at=datetime(2026, 6, 22, 9, 0),
    service="twitter"
)
```

**Parameters:**
- `text` (str): Post content
- `due_at` (str or datetime): When to publish
- `service` (str, optional): Service name

**Returns:** `Dict` - Created post object

### create_image_post()

Create a post with an image.

```python
result = client.create_image_post(
    channel_id="channel_id",
    text="Check this out! 🖼️",
    image_url="https://yoursite.com/image.jpg",
    mode="shareNow"
)
```

**Parameters:**
- `channel_id` (str): Channel ID
- `text` (str): Post content
- `image_url` (str): Public URL to image
- `mode` (str): Publishing mode
- `scheduling_type` (str): Scheduling type
- `due_at` (str, optional): Schedule time

**Returns:** `Dict` - Created post object

---

## Post Management

### get_posts()

Get recent posts for an organization.

```python
posts = client.get_posts(org_id, limit=10)
for edge in posts['edges']:
    post = edge['node']
    print(f"{post['id']}: {post['text'][:50]}...")
```

**Parameters:**
- `organization_id` (str): Organization ID
- `limit` (int): Number of posts to return
- `cursor` (str, optional): Pagination cursor

**Returns:** `Dict` with:
- `edges`: List of post edges
- `pageInfo`: Pagination info

### get_post()

Get specific post by ID.

```python
post = client.get_post("post_id_here")
print(post['text'])
print(post['status'])
```

**Parameters:**
- `post_id` (str): Post ID

**Returns:** `Dict` - Post details

### delete_post()

Delete/unschedule a post.

```python
result = client.delete_post("post_id_here")
```

**Parameters:**
- `post_id` (str): Post ID

**Returns:** `Dict` - Deletion result

**Note:** Buffer GraphQL API does NOT support deleting published posts. This only works for scheduled/queued posts.

---

## Exceptions

### BufferAPIException

Raised when API calls fail.

```python
from scripts.buffer_client import BufferAPIException

try:
    client.post_now("Hello!")
except BufferAPIException as e:
    print(f"Error: {e.message}")
    print(f"Status Code: {e.status_code}")
```

**Attributes:**
- `message` (str): Error message
- `status_code` (int): HTTP status code
- `response` (str or Dict): Full error response

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `BASE_URL` | `"https://api.buffer.com"` | Buffer API base URL |
| `FREE_TIER_LIMIT` | `10` | Free tier queue limit |

---

## Publishing Modes

| Mode | Description | Queue? |
|------|-------------|--------|
| `shareNow` | Post immediately | No |
| `customScheduled` | Schedule for specific time | No |
| `addToQueue` | Add to Buffer's queue | Yes |
| `shareNext` | Post at next slot | Yes |
| `recommendedTime` | Buffer optimizes timing | Yes |

---

## Service Names

| Service | API Name |
|---------|----------|
| Twitter/X | `twitter` |
| Facebook | `facebook` |
| LinkedIn | `linkedin` |
| Instagram | `instagram` |
| Google Business | `googlebusiness` |
| Pinterest | `pinterest` |
| TikTok | `tiktok` |

**Note:** Service availability depends on your Buffer subscription.
