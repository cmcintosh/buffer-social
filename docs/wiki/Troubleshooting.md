# Troubleshooting

This page helps you resolve common issues with Buffer Social.

## Installation Issues

### "No module named 'requests'"

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install requests python-dotenv
# Or
pip install -r requirements.txt
```

### "No module named 'scripts.buffer_client'"

**Error:**
```
ModuleNotFoundError: No module named 'scripts'
```

**Solution:**
Run from project root directory:
```bash
cd /path/to/buffer-social
python -c "from scripts.buffer_client import BufferClient"
```

Or use absolute import:
```python
import sys
sys.path.insert(0, '/path/to/buffer-social')
from scripts.buffer_client import BufferClient
```

---

## Configuration Issues

### "No organizations found"

**Error:**
```
ValueError: No organizations found
```

**Causes:**
1. Invalid access token
2. Token doesn't have organization access
3. Buffer account not properly configured

**Solutions:**

1. Verify your token:
```bash
python -c "
import os
print('Token exists:', bool(os.getenv('BUFFER_ACCESS_TOKEN')))
print('Token length:', len(os.getenv('BUFFER_ACCESS_TOKEN', '')))
"
```

2. Check token at [buffer.com/developers](https://buffer.com/developers)

3. Ensure you have at least one social account connected in Buffer

### "No active channels found"

**Error:**
```
ValueError: No active channels found
```

**Causes:**
1. No social accounts connected to Buffer
2. Social accounts disconnected
3. Wrong service name

**Solutions:**

1. Connect social accounts at [buffer.com](https://buffer.com)
2. Check connected accounts:
```python
from scripts.buffer_client import BufferClient
client = BufferClient()
org_id = client.get_default_organization_id()
channels = client.get_channels(org_id)
print(f"Found {len(channels)} channels")
for c in channels:
    print(f"  - {c['service']}: {c['name']}")
```

3. Use correct service names: `twitter`, `facebook`, `linkedin`, etc.

### "authentication failed"

**Error:**
```
BufferAPIException: GraphQL Error: authentication failed
```

**Solutions:**

1. Regenerate your token:
   - Go to [buffer.com/developers](https://buffer.com/developers)
   - Delete old app
   - Create new app
   - Copy new token

2. Update `.env` file:
```bash
# Remove old token
unset BUFFER_ACCESS_TOKEN

# Edit and save .env
nano .env

# Reload
source .env
```

3. Verify environment loaded:
```python
import os
print(os.getenv('BUFFER_ACCESS_TOKEN'))  # Should show token
```

---

## Posting Issues

### "Posts not appearing immediately"

**Symptom:** Post doesn't show up on social media

**Causes:**
1. Using `addToQueue` mode instead of `shareNow`
2. Scheduled for future date
3. Network issues

**Solutions:**

1. Use `shareNow` mode:
```python
client.post_now("Hello!", service="twitter")  # Immediate
```

2. Check post status:
```python
posts = client.get_posts(org_id, limit=5)
for edge in posts['edges']:
    post = edge['node']
    print(f"ID: {post['id']}")
    print(f"Status: {post['status']}")  # SENT, PENDING, etc.
    print(f"Sent at: {post.get('sentAt', 'Not sent')}")
```

3. Verify in Buffer dashboard: [buffer.com](https://buffer.com)

### "Rate limit exceeded"

**Error:**
```
HTTP Error: 429
```

**Solutions:**

1. Add delays between requests:
```python
import time

for service in ['twitter', 'facebook']:
    client.post_now("Hello!", service=service)
    time.sleep(1)  # Wait 1 second
```

2. Batch posts:
```python
# Instead of posting immediately, collect and post at intervals
posts_to_make = [...]
for post in posts_to_make:
    client.post_now(post['text'])
    time.sleep(2)
```

3. Check your Buffer plan limits

### "Image not appearing"

**Symptom:** Post appears but without image

**Causes:**
1. Image URL not publicly accessible
2. Image format not supported
3. Image too large

**Solutions:**

1. Verify URL is public:
```bash
curl -I https://yoursite.com/image.jpg
# Should return 200 OK
```

2. Check image format (JPG, PNG, GIF supported)

3. Use smaller images (under 5MB recommended)

4. Verify HTTPS (required)

---

## API Errors

### "GraphQL Error: Invalid channel ID"

**Error:**
```
BufferAPIException: GraphQL Error: Invalid channel ID
```

**Solution:**

Get fresh channel IDs:
```python
org_id = client.get_default_organization_id()
channels = client.get_channels(org_id)

for channel in channels:
    print(f"{channel['service']}: {channel['id']}")
```

### "Cannot delete published post"

**Symptom:** `delete_post()` fails

**Cause:** Buffer API doesn't support deleting published posts

**Solution:**
Delete manually from:
- [Twitter](https://twitter.com)
- [Facebook](https://facebook.com)
- [LinkedIn](https://linkedin.com)

Or delete from Buffer dashboard before it's published.

---

## Environment Issues

### ".env file not loading"

**Symptom:** Token not found despite being in `.env`

**Causes:**
1. Running from wrong directory
2. python-dotenv not installed
3. .env file syntax error

**Solutions:**

1. Check current directory:
```bash
pwd
ls -la .env
```

2. Explicitly load dotenv:
```python
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(env_path)

import os
print(os.getenv('BUFFER_ACCESS_TOKEN'))
```

3. Check .env syntax:
```bash
# Correct
BUFFER_ACCESS_TOKEN=your_token_here

# Incorrect (no spaces!)
BUFFER_ACCESS_TOKEN = your_token_here
```

### "SSL certificate verification failed"

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**

Update certificates:
```bash
# macOS
brew install ca-certificates

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# Or temporarily disable (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

---

## Debug Mode

Enable detailed logging:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now use the client
from scripts.buffer_client import BufferClient
client = BufferClient()
```

This will show:
- Full HTTP requests
- Response headers
- API endpoints called

---

## Getting Help

If your issue isn't covered here:

1. **Check Buffer API docs:** [developers.buffer.com](https://developers.buffer.com)

2. **Test with curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.buffer.com/graphql \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ account { email } }"}'
```

3. **Open an issue** on GitHub with:
   - Error message (full traceback)
   - Steps to reproduce
   - Your environment (OS, Python version)

4. **Contact:** cmcintosh@wembassy.com
