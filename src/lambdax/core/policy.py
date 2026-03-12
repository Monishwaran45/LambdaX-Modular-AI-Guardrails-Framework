"""Policy engine for managing guard configurations."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError

from lambdax.core.exceptions import PolicyException

logger = logging.getLogger(__name__)


class GuardConfig(BaseModel):
    """Configuration for a single guard."""

    name: str
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class Policy(BaseModel):
    """Policy definition."""

    id: str
    description: str = ""
    input_guards: List[GuardConfig] = Field(default_factory=list)
    output_guards: List[GuardConfig] = Field(default_factory=list)
    fallback_action: str = "block"  # block, warn, or pass


class PolicyConfig(BaseModel):
    """Root policy configuration."""

    version: int = 1
    policies: List[Policy]


class PolicyEngine:
    """Manages policy loading, validation, and guard resolution."""

    def __init__(self, policy_path: Optional[Path] = None):
        self.policy_path = policy_path
        self.config: Optional[PolicyConfig] = None
        self.guard_registry: Dict[str, type] = {}

        if policy_path:
            self.load_policy(policy_path)

    def load_policy(self, policy_path: Path) -> None:
        """Load and validate policy from YAML file."""
        try:
            with open(policy_path, "r") as f:
                data = yaml.safe_load(f)

            self.config = PolicyConfig(**data)
            logger.info(f"Loaded policy from {policy_path}")

        except FileNotFoundError:
            raise PolicyException(f"Policy file not found: {policy_path}")
        except yaml.YAMLError as e:
            raise PolicyException(f"Invalid YAML in policy file: {e}")
        except ValidationError as e:
            raise PolicyException(f"Policy validation failed: {e}")

    def register_guard(self, name: str, guard_class: type) -> None:
        """Register a guard class."""
        self.guard_registry[name] = guard_class
        logger.debug(f"Registered guard: {name}")

    def get_policy(self, policy_id: str = "default") -> Optional[Policy]:
        """Get policy by ID."""
        if not self.config:
            return None

        for policy in self.config.policies:
            if policy.id == policy_id:
                return policy
        return None

    def get_input_guards(
        self, context: Any, policy_id: str = "default"
    ) -> List[Any]:
        """Get instantiated input guards for a policy."""
        policy = self.get_policy(policy_id)
        if not policy:
            return []

        guards = []
        for guard_config in policy.input_guards:
            if not guard_config.enabled:
                continue

            guard_class = self.guard_registry.get(guard_config.name)
            if guard_class:
                guards.append(guard_class(config=guard_config.config))
            else:
                logger.warning(f"Guard not found in registry: {guard_config.name}")

        return guards

    def get_output_guards(
        self, context: Any, policy_id: str = "default"
    ) -> List[Any]:
        """Get instantiated output guards for a policy."""
        policy = self.get_policy(policy_id)
        if not policy:
            return []

        guards = []
        for guard_config in policy.output_guards:
            if not guard_config.enabled:
                continue

            guard_class = self.guard_registry.get(guard_config.name)
            if guard_class:
                guards.append(guard_class(config=guard_config.config))
            else:
                logger.warning(f"Guard not found in registry: {guard_config.name}")

        return guards
