# Creating Custom Guards

## Overview

LambdaX makes it easy to create custom guards for your specific use cases. This guide walks through the process of building, testing, and deploying custom guards.

## Basic Guard Structure

Every guard must inherit from the `Guard` base class and implement two methods:

```python
from lambdax.core.guard import Guard
from lambdax.core.context import RequestContext
from typing import Optional, Dict, Any

class MyCustomGuard(Guard):
    def _setup(self) -> None:
        """Initialize guard resources (models, patterns, etc.)"""
        pass
    
    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Inspect input text. Return dict if blocked, None if passed."""
        pass
    
    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Inspect output text. Return dict if blocked, None if passed."""
        pass
```

## Example: Keyword Blocker

```python
import re
from typing import Optional, Dict, Any, List
from lambdax.core.guard import Guard
from lambdax.core.context import RequestContext

class KeywordBlockerGuard(Guard):
    """Blocks text containing specific keywords."""
    
    def _setup(self) -> None:
        """Load keywords from config."""
        self.keywords: List[str] = self.config.get("keywords", [])
        self.case_sensitive = self.config.get("case_sensitive", False)
        
    def _find_keywords(self, text: str) -> List[str]:
        """Find matching keywords in text."""
        found = []
        check_text = text if self.case_sensitive else text.lower()
        
        for keyword in self.keywords:
            check_keyword = keyword if self.case_sensitive else keyword.lower()
            if check_keyword in check_text:
                found.append(keyword)
        
        return found
    
    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check input for keywords."""
        found = self._find_keywords(text)
        
        if found:
            return {
                "reason": f"Blocked keywords detected: {', '.join(found)}",
                "keywords": found,
                "guard": self.name
            }
        return None
    
    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check output for keywords."""
        return await self.inspect_input(text, context)
```

## Using ML Models

For guards that use machine learning models:

```python
import asyncio
from transformers import pipeline

class MLGuard(Guard):
    def _setup(self) -> None:
        """Initialize model config."""
        self.model_name = self.config.get("model", "default-model")
        self.threshold = self.config.get("threshold", 0.8)
        self._model = None
    
    async def _load_model(self) -> None:
        """Lazy load model."""
        if self._model is not None:
            return
        
        loop = asyncio.get_event_loop()
        self._model = await loop.run_in_executor(
            None, pipeline, "text-classification", self.model_name
        )
    
    async def _predict(self, text: str) -> float:
        """Run model prediction."""
        if self._model is None:
            await self._load_model()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._model, text)
        return result[0]['score']
```

## Registration

Register your guard with the policy engine:

```python
from lambdax import PolicyEngine

policy_engine = PolicyEngine()
policy_engine.register_guard("my_guard", MyCustomGuard)
```

## Configuration

Add to policy.yaml:

```yaml
policies:
  - id: default
    input_guards:
      - name: my_guard
        enabled: true
        config:
          keywords: ["spam", "scam"]
          case_sensitive: false
```

## Testing

Create unit tests:

```python
import pytest
from lambdax.core.context import RequestContext

@pytest.mark.asyncio
async def test_keyword_blocker():
    guard = KeywordBlockerGuard(config={"keywords": ["spam"]})
    context = RequestContext()
    
    result = await guard.inspect_input("This is spam", context)
    assert result is not None
    assert "spam" in result["keywords"]
    
    result = await guard.inspect_input("Clean text", context)
    assert result is None
```

## Best Practices

1. **Use async/await** for I/O operations
2. **Lazy load models** to reduce cold start time
3. **Handle errors gracefully** - use fail_open config
4. **Return structured results** with reason and metadata
5. **Add comprehensive tests**
6. **Document configuration options**
7. **Consider performance** - cache expensive operations

## Publishing

To make your guard available as a plugin:

```toml
[project.entry-points."lambdax.guards"]
my_guard = "my_package.guards:MyCustomGuard"
```

See [examples/custom_guard.py](../examples/custom_guard.py) for a complete example.
