# LambdaX Architecture

## Overview

LambdaX is built with a modular, async-first architecture designed for production workloads. The framework consists of several key components that work together to provide comprehensive AI guardrails.

## Core Components

### 1. Guard Interface

The `Guard` base class defines the contract for all guards:

```python
class Guard(ABC):
    async def inspect_input(self, text: str, context: RequestContext) -> Optional[Dict]
    async def inspect_output(self, text: str, context: RequestContext) -> Optional[Dict]
```

Key features:
- Async-first design for high concurrency
- Built-in error handling with fail-open/fail-closed modes
- Context propagation for request tracking
- Lazy model loading to reduce cold start time

### 2. Policy Engine

The Policy Engine manages guard configurations and selection:

- YAML-based policy definitions
- Dynamic guard resolution via registry
- Support for multiple policies per deployment
- Hot-reload capability (future)

Policy structure:
```yaml
policies:
  - id: policy_name
    input_guards: [...]
    output_guards: [...]
    fallback_action: block|warn|pass
```

### 3. Orchestrator

The Orchestrator coordinates guard execution:

- Concurrent guard execution using `asyncio.gather()`
- Request-level caching with TTL
- Timeout management
- First-block-wins strategy

Flow:
1. Check cache for previous result
2. Fetch guards from policy engine
3. Execute guards concurrently
4. Process results (first block wins)
5. Cache result

### 4. Request Context

The `RequestContext` object carries metadata through the pipeline:

- Unique request ID for tracing
- User identification
- Custom metadata
- Guard execution results

### 5. Guard Registry

Plugin system for guard discovery:

- Entry points for third-party guards
- Dynamic loading at runtime
- Namespace isolation

## Data Flow

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Orchestrator   │
│  - Check cache  │
│  - Get guards   │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────────┐
│     Concurrent Execution        │
│  ┌────────┐ ┌────────┐ ┌──────┐│
│  │Guard 1 │ │Guard 2 │ │Guard3││
│  └────────┘ └────────┘ └──────┘│
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────┐
│ Result Merger   │
│ (First block)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Response      │
└─────────────────┘
```

## Concurrency Model

LambdaX uses Python's `asyncio` for concurrency:

1. **Guard Execution**: All guards run concurrently
2. **Model Loading**: Models load in thread pool to avoid blocking
3. **API Server**: FastAPI with async handlers
4. **Caching**: Thread-safe TTL cache

## Error Handling

Three-tier error handling:

1. **Guard Level**: Try-catch in guard implementation
2. **Orchestrator Level**: Exception handling with fail-open/fail-closed
3. **API Level**: HTTP error responses with proper status codes

## Observability

Built-in observability features:

- **Logging**: Structured JSON logs with request IDs
- **Metrics**: Prometheus metrics for guard latency, cache hits, errors
- **Tracing**: OpenTelemetry integration for distributed tracing

## Security Considerations

- Input validation at API boundary
- No arbitrary code execution
- Model isolation (separate processes/containers)
- Policy file integrity checks
- Rate limiting per client

## Scalability

Horizontal scaling strategies:

1. **Stateless Design**: No shared state between instances
2. **Caching**: Reduce redundant guard executions
3. **Model Optimization**: Quantization, ONNX runtime
4. **Load Balancing**: Standard HTTP load balancers

## Extension Points

1. **Custom Guards**: Implement `Guard` interface
2. **Custom Policies**: YAML configuration
3. **Custom Models**: Swap model implementations
4. **Custom Caching**: Replace cache backend
5. **Custom Metrics**: Add Prometheus collectors

## Performance Characteristics

Typical latencies (with caching):

- Privacy Guard (regex): <5ms
- Prompt Injection (ML): 50-200ms
- Toxicity (ML): 50-200ms
- Cache hit: <1ms

Throughput: 100-500 requests/second per instance (depends on guards)

## Future Enhancements

- Streaming support for real-time guardrails
- Advanced caching strategies (Redis, Memcached)
- Guard chaining and composition
- A/B testing framework for guards
- Auto-scaling based on load
