"""Base technique class and registry for POE."""

import abc
from typing import Dict, List, Type

# Module-level registry
_REGISTRY: Dict[str, "BaseTechnique"] = {}


def register(cls: Type["BaseTechnique"]) -> Type["BaseTechnique"]:
    """Class decorator that registers a technique by its name attribute."""
    instance = cls()
    if instance.name in _REGISTRY:
        raise ValueError(f"Duplicate technique name: {instance.name}")
    _REGISTRY[instance.name] = instance
    return cls


def get_all_techniques() -> Dict[str, "BaseTechnique"]:
    """Return a shallow copy of the registry."""
    return dict(_REGISTRY)


def get_techniques_by_category(category: str) -> List["BaseTechnique"]:
    return [t for t in _REGISTRY.values() if t.category == category]


def get_technique_by_name(name: str) -> "BaseTechnique":
    if name not in _REGISTRY:
        raise KeyError(f"Unknown technique: {name}. Available: {sorted(_REGISTRY.keys())}")
    return _REGISTRY[name]


class BaseTechnique(abc.ABC):
    """
    Every technique must define:
      - name: str          unique identifier
      - category: str      grouping (encoding, mutation, structural, context)
      - obfuscate(payload: str) -> List[str]
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def category(self) -> str:
        ...

    @abc.abstractmethod
    def obfuscate(self, payload: str) -> List[str]:
        """Return one or more obfuscated variants of the payload."""
        ...

    def __repr__(self) -> str:
        return f"<Technique:{self.name} category={self.category}>"
