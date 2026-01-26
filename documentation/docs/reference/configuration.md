# Configuration

All configuration options for Savanty.

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key for LLM access |

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_LLM_MODEL` | `openai/gpt-4o` | LLM model to use |

**Supported models:**

- `openai/gpt-4o` (recommended)
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo` (faster, less accurate)

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_PORT` | `8000` | Web server port |
| `SAVANTY_ENV` | `development` | Environment mode |
| `SAVANTY_CORS_ORIGINS` | localhost | Allowed CORS origins |

**CORS origins format:**

```bash
# Single origin
SAVANTY_CORS_ORIGINS=https://myapp.com

# Multiple origins (comma-separated)
SAVANTY_CORS_ORIGINS=https://myapp.com,https://api.myapp.com
```

### Request Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_MAX_PROBLEM_LENGTH` | `10000` | Max chars in problem description |
| `SAVANTY_MAX_ADDITIONAL_INFO_LENGTH` | `5000` | Max chars in additional info |
| `SAVANTY_SOLVE_TIMEOUT` | `120` | Solve timeout in seconds |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `SAVANTY_LOG_FORMAT` | See below | Log message format |

**Default log format:**

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Configuration File

Create a `.env` file in your project root:

```bash
# .env
OPENAI_API_KEY=sk-...

# Optional
SAVANTY_LLM_MODEL=openai/gpt-4o
SAVANTY_PORT=8000
SAVANTY_LOG_LEVEL=INFO
```

Load with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

from savanty import solve_optimization_problem
```

## Example Configurations

### Development

```bash
export OPENAI_API_KEY=sk-...
export SAVANTY_ENV=development
export SAVANTY_LOG_LEVEL=DEBUG
```

### Production

```bash
export OPENAI_API_KEY=sk-...
export SAVANTY_ENV=production
export SAVANTY_CORS_ORIGINS=https://yourdomain.com
export SAVANTY_LOG_LEVEL=WARNING
export SAVANTY_SOLVE_TIMEOUT=60
```

### High-Volume

```bash
export OPENAI_API_KEY=sk-...
export SAVANTY_LLM_MODEL=openai/gpt-3.5-turbo  # Faster
export SAVANTY_SOLVE_TIMEOUT=30
export SAVANTY_MAX_PROBLEM_LENGTH=5000
```

## Programmatic Configuration

Set environment variables before importing:

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["SAVANTY_LLM_MODEL"] = "openai/gpt-4o"

from savanty import solve_optimization_problem
```

## Configuration Precedence

1. Environment variables (highest priority)
2. `.env` file (if using python-dotenv)
3. Default values (lowest priority)
