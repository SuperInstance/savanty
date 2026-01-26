# Installation

Savanty can be installed in several ways depending on your needs.

## Requirements

- Python 3.10, 3.11, 3.12, or 3.13
- An OpenAI API key for LLM access

## Installation Methods

=== "uvx (Recommended)"

    Use `uvx` to run Savanty directly without permanent installation:

    ```bash
    # Run the desktop app
    uvx --from 'savanty[desktop]' savanty-desktop

    # Run the web interface
    uvx savanty --web

    # Solve from command line
    uvx savanty -p "Your problem description"
    ```

    To install as a persistent tool:

    ```bash
    uv tool install 'savanty[desktop]'
    savanty-desktop
    ```

=== "pip"

    Install with pip for permanent installation:

    ```bash
    # Core package (CLI, web, Python API)
    pip install savanty

    # With desktop app support
    pip install 'savanty[desktop]'
    ```

=== "From Source"

    Clone and install from the repository:

    ```bash
    git clone https://github.com/skelf-research/savanty.git
    cd savanty
    uv sync                      # Install dependencies
    uv sync --extra desktop      # Add desktop app support
    ```

    Run in development mode:

    ```bash
    uv run savanty --web         # Web interface
    uv run savanty-desktop       # Desktop app
    ```

## Configuration

### Required: OpenAI API Key

Savanty requires an OpenAI API key to function:

```bash
export OPENAI_API_KEY=your_api_key_here
```

Add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence.

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_LLM_MODEL` | `openai/gpt-4o` | LLM model to use |
| `SAVANTY_PORT` | `8000` | Web server port |
| `SAVANTY_LOG_LEVEL` | `INFO` | Logging verbosity |

See [Configuration Reference](reference/configuration.md) for all options.

## Verifying Installation

Check that Savanty is installed correctly:

```bash
# Check version
savanty --version

# Check help
savanty --help

# Test with a simple problem
savanty -p "Assign task A to worker 1 or worker 2"
```

## Platform Notes

### Linux

Savanty works on most Linux distributions. Ensure you have Python 3.10+ installed:

```bash
python3 --version  # Should show 3.10 or higher
```

### macOS

Works on macOS 11 (Big Sur) and later. Install Python via Homebrew if needed:

```bash
brew install python@3.12
```

### Windows

Works on Windows 10 and later. Install Python from [python.org](https://www.python.org/downloads/).

For the desktop app, ensure you have the Visual C++ Redistributable installed.

## Troubleshooting Installation

### "No module named 'savanty'"

The package isn't installed in your current Python environment:

```bash
pip install savanty
```

### "OPENAI_API_KEY not set"

Export your API key before running:

```bash
export OPENAI_API_KEY=your_key_here
```

### Desktop app won't start

The Slint UI library may need additional setup:

```bash
pip install 'savanty[desktop]' --force-reinstall
```

### Permission errors on Linux

You may need to adjust permissions or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install savanty
```

## Next Steps

- [Getting Started](getting-started.md) - Solve your first problem
- [User Guide](user-guide/index.md) - Learn all interface options
- [Configuration](reference/configuration.md) - All configuration options
