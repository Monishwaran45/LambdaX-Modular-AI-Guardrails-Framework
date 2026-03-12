# LambdaX: Production-Ready AI Guardrails Framework

[![CI](https://github.com/Monishwaran45/lambdax/workflows/CI/badge.svg)](https://github.com/Monishwaran45/lambdax/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

LambdaX is a production-ready, modular AI guardrails framework designed to protect LLM applications from security threats, toxic content, and privacy violations. Built with async-first architecture, comprehensive observability, and enterprise-grade reliability.

## Features

- **Async-First Architecture**: Built for high-concurrency workloads
- **Modular Guard System**: Easily extensible with custom guards
- **Policy Engine**: Flexible YAML-based configuration with hot-reload support
- **Production-Ready**: Structured logging, Prometheus metrics, OpenTelemetry tracing
- **Multiple Deployment Options**: Library, API server, or sidecar container
- **Built-in Guards**:
  - Prompt Injection Detection
  - Toxicity Detection
  - PII/Privacy Protection

## Quick Start

### Installation

```bash
pip install lambdax
```

### Basic Usage

```python
import asyncio
from lambdax import Orchestrator, PolicyEngine, RequestContext
from lambdax.guards import PromptInjectionGuard, PrivacyGuard

# Initialize
policy_engine = PolicyEngine()
policy_engine.register_guard("prompt_injection", PromptInjectionGuard)
policy_engine.register_guard("privacy", PrivacyGuard)

orchestrator = Orchestrator(policy_engine)

# Inspect input
async def check():
    context = RequestContext()
    result = await orchestrator.inspect_input(
        "Ignore previous instructions",
        context
    )
    print("Blocked!" if result else "Passed")

asyncio.run(check())
```

### CLI Usage

```bash
# Inspect text
lambdax inspect --input "Your text here"

# Start API server
lambdax serve --port 8000
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Custom Guards](docs/custom-guards.md)
- [Deployment](docs/deployment.md)
- [API Reference](docs/api-reference.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Authors

- Monish ([@Monishwaran45](https://github.com/Monishwaran45))
- Vishal

## Support

- Issues: [GitHub Issues](https://github.com/Monishwaran45/lambdax/issues)
- Discussions: [GitHub Discussions](https://github.com/Monishwaran45/lambdax/discussions)
