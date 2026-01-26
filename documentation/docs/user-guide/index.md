# User Guide

Savanty provides multiple ways to interact with the optimization solver. Choose the interface that best fits your workflow.

## Available Interfaces

### [Desktop App](desktop-app.md)

A native desktop application with a visual interface. Best for:

- Interactive exploration of problems
- Trying different constraints quickly
- Viewing visualizations without a browser

### [Web Interface](web-interface.md)

A browser-based interface with a modern UI. Best for:

- Teams sharing a local deployment
- Integration with existing web workflows
- Accessing from any device on your network

### [Command Line](cli.md)

A terminal-based interface. Best for:

- Quick one-off problem solving
- Scripting and automation
- Integration with shell pipelines

### [Python API](python-api.md)

Direct programmatic access. Best for:

- Building applications that need optimization
- Batch processing multiple problems
- Custom integrations and workflows

## Choosing an Interface

| Use Case | Recommended Interface |
|----------|----------------------|
| Learning Savanty | Desktop App |
| Quick problem solving | CLI or Desktop |
| Building an application | Python API |
| Team deployment | Web Interface |
| Automation | CLI or Python API |

## Common Workflow

Regardless of interface, the workflow is similar:

1. **Describe your problem** in plain English
2. **Answer questions** if Savanty needs clarification
3. **Review the solution** and ASP code
4. **Iterate** if needed with additional constraints

## Tips for Better Results

### Be Specific

Instead of:
> "Schedule some workers"

Say:
> "Schedule 5 workers (Alice, Bob, Carol, Dave, Eve) for morning and evening shifts over Monday through Friday"

### State Constraints Clearly

Instead of:
> "Make sure it's fair"

Say:
> "Each worker should have between 4 and 6 shifts per week"

### Provide Context

If your problem has domain-specific terminology, explain it:

> "Schedule nurses for a hospital ward. A 'handoff' is when one nurse ends their shift and another begins - we want to minimize handoffs."

## Next Steps

- [CLI Usage](cli.md) - Command line interface
- [Web Interface](web-interface.md) - Browser-based interface
- [Desktop App](desktop-app.md) - Native desktop application
- [Python API](python-api.md) - Programmatic access
