# REST API

Savanty exposes a REST API when running in web mode.

## Starting the Server

```bash
savanty --web --port 8000
```

## Endpoints

### POST /solve

Solve an optimization problem.

**Request:**

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Schedule 3 nurses for 2 shifts",
    "additional_info": ""
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `problem_description` | `string` | Yes | Problem in plain English (10-10000 chars) |
| `additional_info` | `string` | No | Answers to questions (max 5000 chars) |

**Response (Success):**

```json
{
  "solution": "assign(alice, day1, morning)...",
  "asp_code": "% Facts\nnurse(alice)...",
  "visualization_html": "<div>...</div>",
  "log": "Problem solved successfully."
}
```

**Response (Needs More Info):**

```json
{
  "needs_more_info": true,
  "questions": [
    "How many nurses are available?",
    "What shifts exist?"
  ],
  "log": "Please provide more information to solve this problem."
}
```

**Response (Not Suitable):**

```json
{
  "not_suitable": true,
  "suggested_tool": "scipy",
  "reason": "This is a continuous optimization problem.",
  "log": "This problem is better suited for a different approach."
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400` | Invalid input or solver error |
| `408` | Request timeout |
| `500` | Internal server error |
| `503` | Service not ready (API key missing) |

### GET /health

Health check endpoint.

**Request:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "0.2.1",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "api": "ok",
    "openai_configured": true
  }
}
```

### GET /ready

Readiness check for load balancers.

**Request:**

```bash
curl http://localhost:8000/ready
```

**Response (Ready):**

```json
{
  "status": "ready"
}
```

**Response (Not Ready):**

```json
{
  "status": "not_ready",
  "reason": "OPENAI_API_KEY not configured"
}
```

Status code: `503` when not ready.

## Error Format

All errors return JSON:

```json
{
  "error": "Description of what went wrong",
  "log": "User-friendly message"
}
```

## Rate Limits

No built-in rate limiting. Implement at your load balancer or API gateway for production.

## CORS

Configured via environment variables:

```bash
# Development (default)
SAVANTY_ENV=development
# Allows localhost origins

# Production
SAVANTY_ENV=production
SAVANTY_CORS_ORIGINS=https://yourdomain.com
```

## OpenAPI Schema

Access the auto-generated OpenAPI schema:

```bash
curl http://localhost:8000/openapi.json
```

Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Client Examples

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/solve",
    json={
        "problem_description": "Schedule nurses...",
        "additional_info": ""
    }
)
data = response.json()
print(data["solution"])
```

### JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8000/solve", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    problem_description: "Schedule nurses...",
    additional_info: ""
  })
});
const data = await response.json();
console.log(data.solution);
```

### cURL

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Assign 3 tasks to 2 workers"}'
```
