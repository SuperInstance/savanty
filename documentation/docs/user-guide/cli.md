# CLI Usage

The Savanty command-line interface provides quick access to the optimization solver from your terminal.

## Basic Usage

```bash
savanty -p "Your problem description"
```

## Commands and Options

### Solve a Problem

```bash
savanty -p "Schedule 3 workers for 2 shifts"
savanty --problem "Assign tasks to machines"
```

### Start Web Interface

```bash
savanty --web                    # Default port 8000
savanty --web --port 3000        # Custom port
savanty -w -p 3000               # Short form
```

### Run as MCP Server

For Model Context Protocol integration:

```bash
savanty --mcp
savanty -m
```

### Show Version

```bash
savanty --version
```

### Show Help

```bash
savanty --help
```

## Interactive Mode

When Savanty needs more information, it enters interactive mode:

```
$ savanty -p "Schedule nurses for shifts"

I need more information to solve this problem:
1. How many nurses are available?
2. What shifts exist?
3. How many days should the schedule cover?

Please provide the missing information: 4 nurses, morning/afternoon/night shifts, 7 days
```

The solver continues with your additional information.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - solution found |
| 1 | Error - problem couldn't be solved |

## Examples

### Simple Scheduling

```bash
savanty -p "Schedule Alice and Bob for morning and evening shifts on Monday and Tuesday. Each shift needs one person, no one works both shifts on the same day."
```

### With Pipe

```bash
echo "Assign 3 tasks to 2 workers" | savanty -p -
```

### In a Script

```bash
#!/bin/bash
PROBLEM="Schedule maintenance for 5 machines over 3 days"
RESULT=$(savanty -p "$PROBLEM")
echo "Solution: $RESULT"
```

## Environment Variables

Set these before running:

```bash
export OPENAI_API_KEY=your_key_here
export SAVANTY_LLM_MODEL=openai/gpt-4o
export SAVANTY_PORT=8000
export SAVANTY_LOG_LEVEL=INFO
```

## Common Issues

### "OPENAI_API_KEY not configured"

Set your API key:

```bash
export OPENAI_API_KEY=your_key_here
```

### Problem Timeout

For complex problems, increase the timeout:

```bash
export SAVANTY_SOLVE_TIMEOUT=300  # 5 minutes
savanty -p "Complex scheduling problem..."
```

### "Not suitable for ASP"

Some problems are better solved with other tools. Savanty will suggest alternatives:

```
This problem is better suited for a different tool.
Reason: This appears to be a continuous optimization problem.
Suggested tool: scipy (pip install scipy)
```

## Tips

1. **Quote your problem** to preserve spaces and special characters
2. **Use multi-line input** for complex problems by using quotes
3. **Check logs** with `SAVANTY_LOG_LEVEL=DEBUG` for troubleshooting
