# Web Interface

The Savanty web interface provides a modern, browser-based experience for solving optimization problems.

## Starting the Server

```bash
savanty --web
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### Custom Port

```bash
savanty --web --port 3000
```

### Production Deployment

For production environments, configure CORS:

```bash
export SAVANTY_ENV=production
export SAVANTY_CORS_ORIGINS=https://yourdomain.com
savanty --web
```

## Interface Overview

### Problem Input

The main text area accepts your problem description in plain English. Enter your constraints, requirements, and objectives here.

### Example Selector

Quick-start buttons load pre-written example problems:

- **Nurse Scheduling** - Hospital shift scheduling
- **Delivery Routing** - Route optimization with time windows
- **Team Formation** - Skill-based team building
- **Wedding Seating** - Event seating with constraints

### Results Tabs

After solving, view results in three tabs:

1. **Visualization** - A formatted display of your solution
2. **Raw Output** - The ASP solver's raw answer set
3. **ASP Code** - The generated logic program

## Workflow

1. **Enter your problem** in the text area
2. **Click "Solve"** to submit
3. **Answer questions** if clarification is needed
4. **Review results** in the tabs

## Question Flow

If Savanty needs more information, a question panel appears:

- Answer each question in the provided fields
- Click "Submit Answers" to continue
- The solver uses your answers to refine the problem

## API Access

The web interface exposes a REST API at the same address:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Schedule 2 workers for 2 shifts"}'
```

See [REST API Reference](../reference/rest-api.md) for details.

## Health Checks

For monitoring and load balancers:

- `GET /health` - Basic health status
- `GET /ready` - Readiness check (verifies API key)

```bash
curl http://localhost:8000/health
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVANTY_PORT` | `8000` | Server port |
| `SAVANTY_CORS_ORIGINS` | localhost | Allowed origins (comma-separated) |
| `SAVANTY_ENV` | `development` | Environment mode |

## Browser Compatibility

The web interface works in modern browsers:

- Chrome 90+
- Firefox 90+
- Safari 15+
- Edge 90+

## Tips

- **Use the examples** to understand the expected input format
- **Check the ASP tab** to understand how your problem was encoded
- **Bookmark problems** by saving the URL with your input
