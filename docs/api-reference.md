# API Reference

## REST API Endpoints

### POST /v1/inspect

Inspect text through configured guards.

**Request Body:**

```json
{
  "text": "string (required)",
  "direction": "input|output (default: input)",
  "policy_id": "string (default: default)",
  "user_id": "string (optional)",
  "metadata": {
    "key": "value"
  }
}
```

**Response:**

```json
{
  "blocked": true,
  "reason": "Prompt injection detected",
  "details": {
    "guard": "PromptInjectionGuard",
    "score": 0.95,
    "threshold": 0.8
  },
  "request_id": "uuid"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 500: Server error

### POST /v1/clear-cache

Clear the orchestrator cache.

**Response:**

```json
{
  "status": "cache cleared"
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### GET /metrics

Prometheus metrics endpoint.

## Python API

### Core Classes

#### Orchestrator

```python
from lambdax import Orchestrator

orchestrator = Orchestrator(
    policy_engine,
    cache_ttl=300,
    cache_maxsize=1000,
    timeout=5.0
)

# Inspect input
result = await orchestrator.inspect_input(text, context, policy_id="default")

# Inspect output
result = await orchestrator.inspect_output(text, context, policy_id="default")

# Clear cache
orchestrator.clear_cache()
```

#### PolicyEngine

```python
from lambdax import PolicyEngine
from pathlib import Path

# Load from file
policy_engine = PolicyEngine(Path("policy.yaml"))

# Register guards
policy_engine.register_guard("my_guard", MyGuardClass)

# Get policy
policy = policy_engine.get_policy("default")
```

#### RequestContext

```python
from lambdax import RequestContext

context = RequestContext(
    request_id="optional-id",
    user_id="user123",
    metadata={"source": "api"}
)

# Access results
guard_results = context.guard_results
```

#### Guard

```python
from lambdax.core.guard import Guard

class MyGuard(Guard):
    def _setup(self):
        # Initialize
        pass
    
    async def inspect_input(self, text, context):
        # Return dict if blocked, None if passed
        return None
    
    async def inspect_output(self, text, context):
        return None
```

### Built-in Guards

#### PromptInjectionGuard

```python
from lambdax.guards import PromptInjectionGuard

guard = PromptInjectionGuard(config={
    "threshold": 0.8,
    "model": "protectai/deberta-v3-base-prompt-injection",
    "fail_open": False
})
```

#### ToxicityGuard

```python
from lambdax.guards import ToxicityGuard

guard = ToxicityGuard(config={
    "threshold": 0.7,
    "model": "unitary/toxic-bert",
    "fail_open": False
})
```

#### PrivacyGuard

```python
from lambdax.guards import PrivacyGuard

guard = PrivacyGuard(config={
    "pii_types": ["EMAIL", "PHONE", "SSN", "CREDIT_CARD"],
    "fail_open": False
})
```

## CLI Commands

### inspect

```bash
lambdax inspect --input "text" --policy default --direction input
```

Options:
- `--input, -i`: Text to inspect (required)
- `--policy, -p`: Policy ID (default: default)
- `--direction, -d`: input or output (default: input)
- `--policy-file`: Path to policy file
- `--debug`: Enable debug logging

### serve

```bash
lambdax serve --host 0.0.0.0 --port 8000 --reload
```

Options:
- `--host`: Host to bind (default: 0.0.0.0)
- `--port`: Port to bind (default: 8000)
- `--reload`: Enable auto-reload
- `--debug`: Enable debug logging
