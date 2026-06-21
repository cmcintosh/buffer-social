# Security

This page covers security best practices for using Buffer Social in production environments.

## API Token Security

### Token Scope

Buffer access tokens grant full access to:
- Post to all connected social accounts
- Access posting history
- View connected account information
- Modify queue and scheduled posts

**⚠️ If compromised**, an attacker could post to your social media accounts.

### Secure Storage

#### Environment Variables (Development)

```bash
# .env file (already in .gitignore)
BUFFER_ACCESS_TOKEN=your_token_here
```

Load with python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Production Secrets Management

For production deployments:

**AWS Secrets Manager:**
```python
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='buffer-api-token')
token = response['SecretString']
```

**HashiCorp Vault:**
```python
import hvac

client = hvac.Client(url='https://vault.example.com')
token = client.secrets.kv.v2.read_secret_version(
    path='buffer/api-token'
)['data']['data']['token']
```

**Kubernetes Secrets:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: buffer-api-token
stringData:
  BUFFER_ACCESS_TOKEN: your_token_here
```

### Token Rotation

Rotate tokens periodically (recommended every 90 days):

1. Generate new token at [buffer.com/developers](https://buffer.com/developers)
2. Update secrets store with new token
3. Verify new token works
4. Revoke old token
5. Monitor for any failures

### Monitoring

Watch for suspicious activity:

```python
# Log all API calls
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('buffer_client')

# Log successful posts
logger.info(f"Post created: {result['post']['id']} to {channel['service']}")

# Log failures
logger.error(f"Post failed: {str(exception)}")
```

**Alert on:**
- Unusual posting patterns (high volume, off-hours)
- Posts to unexpected channels
- Failed authentication attempts
- API rate limit exceeded

## Content Validation

Always validate content before posting:

```python
def validate_post(text: str, max_length: int = 280) -> tuple[bool, str]:
    """
    Validate post content.
    
    Returns: (is_valid, error_message)
    """
    # Check length (Twitter limit)
    if len(text) > max_length:
        return False, f"Text exceeds {max_length} characters"
    
    # Check for secrets accidentally included
    sensitive_patterns = [
        r'ghp_[a-zA-Z0-9]{36}',      # GitHub token
        r'sk-[a-zA-Z0-9]{48}',        # OpenAI key
        r'AKIA[0-9A-Z]{16}',           # AWS key
        r'[a-zA-Z0-9]{32}',            # Generic 32-char token
    ]
    
    import re
    for pattern in sensitive_patterns:
        if re.search(pattern, text):
            return False, "Possible secret/token detected in content"
    
    # Check for profanity (optional)
    # blocked_words = ['word1', 'word2']
    
    return True, ""

# Usage
is_valid, error = validate_post("Hello World!")
if is_valid:
    client.post_now("Hello World!")
else:
    print(f"Validation failed: {error}")
```

## Image URL Security

### URL Validation

```python
from urllib.parse import urlparse

def validate_image_url(url: str) -> bool:
    """Ensure image URL is safe."""
    parsed = urlparse(url)
    
    # Require HTTPS
    if parsed.scheme != 'https':
        return False
    
    # Check allowed domains (optional)
    allowed_domains = ['yoursite.com', 'cdn.example.com']
    if parsed.netloc not in allowed_domains:
        return False
    
    # Check file extension
    if not parsed.path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return False
    
    return True
```

### URL Sanitization

Never include sensitive data in image URLs:

```python
# ❌ BAD: Token in URL
image_url = f"https://api.example.com/image?token={api_token}"

# ✅ GOOD: Clean URL
image_url = "https://cdn.example.com/images/post.jpg"
```

## Access Control

### Role-Based Access

Restrict who can post:

```python
class SocialMediaController:
    ALLOWED_ROLES = ['admin', 'social_manager']
    
    def post(self, user, content):
        if user.role not in self.ALLOWED_ROLES:
            raise PermissionError("User not authorized to post")
        
        return self.buffer_client.post_now(content)
```

### Audit Logging

Track all social media activity:

```python
import json
from datetime import datetime

def log_post(user_id, content, channels, result):
    """Log post for audit purposes."""
    audit_log = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'content': content[:100],  # Truncate for privacy
        'channels': channels,
        'post_id': result.get('post', {}).get('id'),
        'ip_address': get_client_ip()
    }
    
    with open('/var/log/social_media.log', 'a') as f:
        f.write(json.dumps(audit_log) + '\n')
```

## Testing Security

### Separate Test Accounts

Never use production credentials for testing:

```python
# config.py
import os

if os.getenv('ENVIRONMENT') == 'production':
    BUFFER_TOKEN = os.getenv('PROD_BUFFER_TOKEN')
else:
    BUFFER_TOKEN = os.getenv('TEST_BUFFER_TOKEN')
```

### Test Environment

Set up dedicated test channels:
- Create test social media accounts
- Connect to separate Buffer app
- Use for development/testing only
- Don't post real content to test channels

## Incident Response

### Token Compromised?

1. **Immediately revoke** the token at [buffer.com/developers](https://buffer.com/developers)
2. **Check** your Buffer dashboard for unauthorized posts
3. **Delete** any unauthorized posts
4. **Generate** new token
5. **Update** all systems with new token
6. **Review** logs for suspicious activity
7. **Notify** stakeholders if necessary

### Unauthorized Post?

1. **Document** the post (screenshot, content, time)
2. **Delete** from social platforms if possible
3. **Check** application logs
4. **Review** recent token usage
5. **Rotate** token immediately
6. **Implement** additional validation

## Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] No credentials in repository
- [ ] Production tokens in secure store
- [ ] Token rotation schedule (90 days)
- [ ] Content validation in place
- [ ] Image URL validation enabled
- [ ] Role-based access control
- [ ] Audit logging configured
- [ ] Separate test environment
- [ ] Monitoring alerts configured
- [ ] Incident response plan documented

## Additional Resources

- [Buffer API Security](https://developers.buffer.com/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

## Reporting Issues

If you discover a security vulnerability:

1. Do NOT open a public issue
2. Email: cmcintosh@wembassy.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
