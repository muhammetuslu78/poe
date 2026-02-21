"""Technique registry - importing submodules triggers @register decorators."""

from techniques import encoding, mutation, structural, context  # noqa: F401
from techniques.base import get_all_techniques, get_techniques_by_category, get_technique_by_name  # noqa: F401
