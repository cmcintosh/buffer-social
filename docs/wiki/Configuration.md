# Configuration

## Getting Your Buffer Access Token

To use the Buffer API, you need an access token from Buffer:

### Step 1: Create a Buffer App

1. Go to [buffer.com/developers](https://buffer.com/developers)
2. Sign in with your Buffer account
3. Click **"Create App"**
4. Fill in the app details:
   - **App Name**: Your project name (e.g., "Wembassy Social")
   - **Description**: Brief description of your use case
   - **Website**: Your company website

### Step 2: Get Your Token

Once the app is created:
1. Click on your app name
2. Copy the **Access Token**
3. Keep this token secure - it grants full access to your Buffer account

### Step 3: Configure Your Environment

Edit the `.env` file in your project root:

```bash
# Required: Your Buffer API access token
BUFFER_ACCESS_TOKEN=your_actual_token_here

# Optional: Default profile IDs (comma-separated)
# Find these using: python scripts/buffer_client.py channels
BUFFER_DEFAULT_PROFILES=
```

**⚠️ Security Warning**: Never commit your `.env` file to version control. It should already be in `.gitignore`.

## Finding Your Channel IDs

Channels (social accounts) have unique IDs. To find yours:

### Via Python

```python
from scripts.buffer_client import BufferClient

client = BufferClient()
org_id = client.get_default_organization_id()
channels = client.get_channels(org_id)

for channel in channels:
    print(f"{channel['service']}: {channel['id']} ({channel['name']})")
```

### Via CLI

```bash
python scripts/buffer_client.py channels
```

### Example Output

```
twitter: abc123xyz (Wembassy)
facebook: def456uvw (Wembassy)
googlebusiness: ghi789rst (Wembassy LLC)
```

## Understanding Publishing Modes

Buffer supports several publishing modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| `shareNow` | Post immediately | ✅ **Recommended** |
| `customScheduled` | Schedule for specific time | Future dated content |
| `addToQueue` | Add to Buffer's queue | Not recommended (limited to 10) |
| `shareNext` | Post at next queue slot | Rarely used |
| `recommendedTime` | Buffer optimizes timing | Rarely used |

## Free Tier Limits

Buffer's free tier includes:
- **3 connected social accounts**
- **10 posts in queue**
- Basic analytics

**Strategy**: Use `shareNow` mode to bypass the queue limit entirely. Keep your content calendar local and push to Buffer only when ready to publish.

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `BUFFER_ACCESS_TOKEN` | ✅ Yes | Your Buffer API access token |
| `BUFFER_DEFAULT_PROFILES` | ❌ No | Comma-separated default profile IDs |

## Testing Your Configuration

Verify everything is set up correctly:

```bash
# Should list your connected channels
python scripts/buffer_client.py channels
```

If you see your channels, you're configured correctly!

## Security Best Practices

See [[Security]] for detailed guidelines on:
- Token rotation
- Secure storage
- Access control
- Monitoring
