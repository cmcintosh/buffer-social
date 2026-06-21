# Buffer Social Media Scheduler

A Python-based OpenClaw skill for cross-platform social media publishing via the Buffer GraphQL API v2.

## 📚 Documentation

Comprehensive documentation is available in the [Wiki](https://github.com/cmcintosh/buffer-social/wiki) or in the [`docs/wiki/`](docs/wiki/) directory:

- **[Home](docs/wiki/Home.md)** - Overview and quick links
- **[Installation](docs/wiki/Installation.md)** - Setup guide
- **[Configuration](docs/wiki/Configuration.md)** - API token and environment setup
- **[Getting Started](docs/wiki/Getting-Started.md)** - Your first post
- **[API Reference](docs/wiki/API-Reference.md)** - Complete method documentation
- **[Security](docs/wiki/Security.md)** - Best practices and security guidelines
- **[Troubleshooting](docs/wiki/Troubleshooting.md)** - Common issues and solutions

## Quick Start

```python
from scripts.buffer_client import BufferClient

client = BufferClient()
client.post_now("Hello World! 🚀", service="twitter")
```

## Features

- ✅ **Multi-platform posting** - Twitter/X, Facebook, LinkedIn, Instagram, Google Business
- ✅ **Immediate or scheduled publishing** - Local calendar control
- ✅ **Media support** - Image attachments
- ✅ **CLI interface** - Command-line tool
- ✅ **Python API** - Library integration

## Requirements

- Python 3.7+
- Buffer account with API access
- See [requirements.txt](requirements.txt)

## Setup

```bash
# Clone repository
git clone https://github.com/cmcintosh/buffer-social.git
cd buffer-social

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Buffer API token
```

## Security Notice

**⚠️ Important**: Never commit your `BUFFER_ACCESS_TOKEN` to version control. The `.env` file is already in `.gitignore`.

See [docs/wiki/Security.md](docs/wiki/Security.md) for detailed security guidelines.

## License

Internal use for Wembassy operations.

---

*For detailed documentation, visit the [Wiki](https://github.com/cmcintosh/buffer-social/wiki) or see the [`docs/wiki/`](docs/wiki/) directory.*
