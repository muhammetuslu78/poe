"""Stateless validation functions for POE."""

import os


def validate_file_readable(path: str) -> str:
    """Return canonical path or raise ValueError."""
    resolved = os.path.abspath(path)
    if not os.path.isfile(resolved):
        raise ValueError(f"File not found: {resolved}")
    if not os.access(resolved, os.R_OK):
        raise ValueError(f"File not readable: {resolved}")
    return resolved


def validate_utf8(data: bytes) -> str:
    """Decode bytes as UTF-8, raise ValueError on failure."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Input is not valid UTF-8: {e}")


def validate_multiplier(value: int) -> int:
    if not isinstance(value, int) or value < 1 or value > 20:
        raise ValueError(f"Multiplier must be an integer between 1 and 20, got: {value}")
    return value


def validate_format(fmt: str) -> str:
    fmt = fmt.lower().strip()
    if fmt not in ("text", "json"):
        raise ValueError(f"Unsupported format: {fmt}. Use 'text' or 'json'.")
    return fmt
