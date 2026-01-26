# MCP Integration

Savanty can run as a Model Context Protocol (MCP) server, allowing integration with AI assistants like Claude.

## What is MCP?

Model Context Protocol is a standard for connecting AI assistants to external tools and data sources. When Savanty runs as an MCP server, AI assistants can directly invoke it to solve optimization problems.

## Starting the MCP Server

```bash
savanty --mcp
```

The server communicates via stdin/stdout using the MCP protocol.

## Available Tools

### `solve_optimization`

Solves an optimization problem described in natural language.

**Input:**

```json
{
  "problem": "Schedule 3 nurses for shifts over 5 days"
}
```

**Output:**

```
Solution: assign(alice, day1, morning), assign(bob, day1, afternoon)...
```

Or on error:

```
Error: OPENAI_API_KEY not configured
```

## Integration with Claude Desktop

Add Savanty to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "savanty": {
      "command": "savanty",
      "args": ["--mcp"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

After configuration, Claude can use Savanty to solve optimization problems directly in conversations.

## Usage in Claude

Once configured, you can ask Claude:

> "Use Savanty to schedule 4 employees for morning and evening shifts this week"

Claude will invoke Savanty's MCP tool and present the solution.

## Requirements

- FastMCP package (included with Savanty)
- Valid OpenAI API key
- Claude Desktop or other MCP-compatible client

## Troubleshooting

### "fastmcp package not installed"

Install the missing dependency:

```bash
pip install fastmcp
```

Or reinstall Savanty:

```bash
pip install savanty --force-reinstall
```

### Server doesn't respond

Check that:

1. `OPENAI_API_KEY` is set in the MCP server environment
2. The command path is correct
3. No other process is blocking stdin/stdout

### Testing the MCP Server

Test manually:

```bash
echo '{"method": "tools/list"}' | savanty --mcp
```

Should return the available tools.
