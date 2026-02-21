"""Streaming input file reader for POE."""

import logging
from typing import Iterator

from utils.validators import validate_file_readable

logger = logging.getLogger(__name__)


def read_payloads(filepath: str) -> Iterator[str]:
    """Yield non-empty, non-comment lines from a UTF-8 text file."""
    filepath = validate_file_readable(filepath)
    with open(filepath, "r", encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, 1):
            line = raw_line.rstrip("\n\r")
            if not line or line.lstrip().startswith("#"):
                logger.debug("Skipping line %d (empty or comment)", line_num)
                continue
            yield line
