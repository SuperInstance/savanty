# Troubleshooting

Solutions to common issues with Savanty.

## Installation Issues

### "No module named 'savanty'"

**Cause:** Package not installed in current environment.

**Solution:**

```bash
pip install savanty
```

If using a virtual environment, make sure it's activated:

```bash
source venv/bin/activate
pip install savanty
```

### "Slint not found" (Desktop App)

**Cause:** Desktop extras not installed.

**Solution:**

```bash
pip install 'savanty[desktop]' --force-reinstall
```

### Permission errors on Linux

**Cause:** System Python has restricted permissions.

**Solution:** Use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install savanty
```

## Configuration Issues

### "OPENAI_API_KEY not configured"

**Cause:** API key environment variable not set.

**Solution:**

```bash
export OPENAI_API_KEY=your_key_here
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

### Invalid API key

**Cause:** API key is malformed or expired.

**Solution:**

1. Check your key at [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Regenerate if expired
3. Ensure no extra spaces in the key

### Web server won't start

**Cause:** Port already in use.

**Solution:**

```bash
# Use different port
savanty --web --port 3000

# Or find and kill the process using port 8000
lsof -i :8000
kill <PID>
```

## Solver Issues

### "This problem is not suitable for ASP"

**Cause:** Your problem type doesn't fit constraint satisfaction.

**What to do:**

- Check the [When to Use Savanty](concepts/when-to-use.md) guide
- Try rephrasing as discrete choices/assignments
- Use the suggested alternative tool

### "No solution found"

**Cause:** Constraints are unsatisfiable.

**Solutions:**

1. **Relax constraints:** Remove or soften some requirements
2. **Check for conflicts:** Two constraints may contradict
3. **Add resources:** Maybe you need more workers/time slots

Example: "Each shift needs 2 nurses, but only 3 nurses for 2 shifts" is unsatisfiable.

### Request timeout

**Cause:** Problem too complex or LLM response slow.

**Solutions:**

```bash
# Increase timeout
export SAVANTY_SOLVE_TIMEOUT=300

# Simplify the problem
# - Reduce number of entities
# - Remove some constraints
# - Break into smaller sub-problems
```

### Incorrect solution

**Cause:** Ambiguous problem description.

**Solutions:**

1. Be more specific in your description
2. Check the generated ASP code - it shows how your problem was interpreted
3. Rephrase constraints more clearly

## Frontend Issues

### Visualization not showing

**Cause:** HTML generation failed or browser compatibility.

**Solutions:**

1. Check the "Raw Output" tab for the solution
2. Try a different browser
3. Check browser console for JavaScript errors

### CORS errors in browser

**Cause:** Running frontend and backend on different origins.

**Solution:**

```bash
# Development
export SAVANTY_ENV=development
# Allows localhost by default

# Production
export SAVANTY_CORS_ORIGINS=https://yourdomain.com
```

## Performance Issues

### Slow response times

**Causes:**

- Large problem size
- Complex constraints
- Network latency to OpenAI

**Solutions:**

1. **Simplify:** Reduce entities or constraints
2. **Faster model:** Use `SAVANTY_LLM_MODEL=openai/gpt-3.5-turbo`
3. **Lower timeout:** Fail fast on impossible problems

### High API costs

**Solutions:**

1. Use a smaller model for development
2. Cache results for repeated problems
3. Batch similar problems

## Getting Help

### Debug logging

Enable verbose logging:

```bash
export SAVANTY_LOG_LEVEL=DEBUG
savanty -p "Your problem"
```

### Check version

```bash
savanty --version
```

### Report issues

Open an issue at: [github.com/skelf-research/savanty/issues](https://github.com/skelf-research/savanty/issues)

Include:

- Savanty version
- Python version
- Full error message
- Problem description (if not sensitive)

## FAQ

### Can I use a different LLM?

Currently, Savanty supports OpenAI models. Other providers may work with DSPy configuration but aren't officially supported.

### How much does it cost?

Savanty uses OpenAI's API. Costs depend on:

- Model choice (GPT-4o vs GPT-3.5-turbo)
- Problem complexity (more tokens = more cost)
- Number of problems solved

Typical problem: $0.01-0.05 with GPT-4o.

### Is my data sent to OpenAI?

Yes, your problem description is sent to OpenAI's API for processing. Don't include sensitive/private data in problem descriptions.

### Can I run it offline?

No, Savanty requires an internet connection to access the LLM API. The ASP solver (Clingo) runs locally, but problem understanding needs the LLM.

### How large can problems be?

Practical limits:

- ~100 entities (workers, tasks, etc.)
- ~50 constraints
- Input text up to 10,000 characters

Larger problems may timeout or produce suboptimal results.
