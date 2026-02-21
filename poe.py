#!/usr/bin/env python3
"""Payload Obfuscation Engine (POE) - CLI entry point.

This tool is designed for authorized penetration testing,
security research, and educational purposes only.
"""

import argparse
import logging
import sys
import time

# Ensure the package is importable when running as a script
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import ObfuscationEngine, SECURITY_DISCLAIMER
from core.input_handler import read_payloads
from core.output_handler import write_text, write_json
from techniques import get_all_techniques
from utils.validators import validate_multiplier, validate_format


def build_parser() -> argparse.ArgumentParser:
    technique_names = ", ".join(sorted(get_all_techniques().keys()))

    parser = argparse.ArgumentParser(
        prog="poe",
        description="Payload Obfuscation Engine (POE) - Security payload obfuscation tool",
        epilog=SECURITY_DISCLAIMER,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Input file path (one payload per line)",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "-m", "--multiplier", type=int, default=5,
        help="Variants per payload, 1-20 (default: 5)",
    )
    parser.add_argument(
        "-f", "--format", default="text", choices=["text", "json"],
        help="Output format (default: text)",
    )
    parser.add_argument(
        "-t", "--techniques", nargs="+", default=None,
        help=f"Techniques to use (default: all). Available: {technique_names}",
    )
    parser.add_argument(
        "-p", "--preserve", action="store_true",
        help="Include original payload in output",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose logging",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Security disclaimer on every run (to stderr)
    sys.stderr.write(SECURITY_DISCLAIMER + "\n")

    # Logging setup - all to stderr to keep stdout clean
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    # Validate arguments
    try:
        validate_multiplier(args.multiplier)
        validate_format(args.format)
    except ValueError as e:
        parser.error(str(e))

    # Build engine
    try:
        engine = ObfuscationEngine(
            multiplier=args.multiplier,
            technique_names=args.techniques,
            preserve_original=args.preserve,
            verbose=args.verbose,
        )
    except (KeyError, ValueError) as e:
        parser.error(str(e))

    # Process pipeline
    start = time.monotonic()
    payloads = read_payloads(args.input)
    results = engine.process_stream(payloads)

    if args.format == "json":
        write_json(results, args.output)
    else:
        write_text(results, args.output)

    elapsed = time.monotonic() - start
    logging.getLogger("poe").info("Completed in %.2f seconds", elapsed)


if __name__ == "__main__":
    main()
