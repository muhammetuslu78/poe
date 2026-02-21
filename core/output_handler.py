"""Output writers for POE (text and JSON formats)."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Iterator, Optional, Tuple

logger = logging.getLogger(__name__)


def write_text(
    results: Iterator[Tuple[str, str, str, str]],
    output_path: Optional[str] = None,
) -> None:
    """Write one obfuscated payload per line."""
    fh = open(output_path, "w", encoding="utf-8") if output_path else sys.stdout
    try:
        count = 0
        for _, obfuscated, _, _ in results:
            fh.write(obfuscated + "\n")
            count += 1
        logger.info("Wrote %d obfuscated payloads (text format)", count)
    finally:
        if fh is not sys.stdout:
            fh.close()


def write_json(
    results: Iterator[Tuple[str, str, str, str]],
    output_path: Optional[str] = None,
) -> None:
    """Write JSON array with metadata, streaming one object at a time."""
    fh = open(output_path, "w", encoding="utf-8") if output_path else sys.stdout
    try:
        fh.write("[\n")
        first = True
        count = 0
        for original, obfuscated, technique, category in results:
            if not first:
                fh.write(",\n")
            entry = {
                "original": original,
                "obfuscated": obfuscated,
                "technique": technique,
                "technique_category": category,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            fh.write("  " + json.dumps(entry, ensure_ascii=False))
            first = False
            count += 1
        fh.write("\n]\n")
        logger.info("Wrote %d obfuscated payloads (JSON format)", count)
    finally:
        if fh is not sys.stdout:
            fh.close()
