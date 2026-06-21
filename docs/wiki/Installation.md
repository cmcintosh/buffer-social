# Installation

## Prerequisites

Before installing, ensure you have:

- **Python 3.7+** installed
- **Git** installed
- A **Buffer account** (free tier available)
- A **Buffer API access token**

## Step 1: Clone the Repository

```bash
git clone https://github.com/cmcintosh/buffer-social.git
cd buffer-social
```

## Step 2: Create Virtual Environment

Creating a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

You should see `(venv)` in your prompt indicating the environment is active.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` >= 2.31.0 - For HTTP requests to Buffer API
- `python-dotenv` >= 1.0.0 - For loading environment variables

## Step 4: Verify Installation

Test that the client can be imported:

```bash
python -c "from scripts.buffer_client import BufferClient; print('✅ Installation successful!')"
```

If you see an error about missing `BUFFER_ACCESS_TOKEN`, that's expected - we'll configure that next.

## Step 5: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials (see [[Configuration]]).

## Next Steps

- [[Configuration]] - Set up your API token
- [[Getting Started]] - Create your first post
- [[API Reference]] - Explore all available methods
