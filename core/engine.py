"""Main obfuscation orchestrator for POE."""

import logging
import random
from typing import Iterator, List, Optional, Set, Tuple

from techniques.base import get_all_techniques, get_technique_by_name, BaseTechnique

logger = logging.getLogger(__name__)

SECURITY_DISCLAIMER = """
===========================================================================
  DISCLAIMER: This tool generates obfuscated payloads for AUTHORIZED
  security testing and research purposes ONLY. Misuse of this tool for
  unauthorized access or malicious activity is illegal and unethical.
  The authors accept no liability for misuse.
===========================================================================
"""


class ObfuscationEngine:
    def __init__(
        self,
        multiplier: int = 5,
        technique_names: Optional[List[str]] = None,
        preserve_original: bool = False,
        verbose: bool = False,
    ):
        self.multiplier = multiplier
        self.preserve_original = preserve_original
        self.verbose = verbose

        if technique_names:
            self.techniques = [get_technique_by_name(n) for n in technique_names]
        else:
            self.techniques = list(get_all_techniques().values())

        if not self.techniques:
            raise ValueError("No techniques available")

        logger.info(
            "Engine initialized: multiplier=%d, techniques=%d (%s)",
            self.multiplier,
            len(self.techniques),
            ", ".join(t.name for t in self.techniques),
        )

    def process_payload(self, payload: str) -> List[Tuple[str, str, str, str]]:
        """
        Generate self.multiplier unique obfuscated variants for a single payload.
        Returns list of (original, obfuscated, technique_name, category).
        """
        seen: Set[str] = set()
        results: List[Tuple[str, str, str, str]] = []
        target = self.multiplier

        if self.preserve_original:
            results.append((payload, payload, "original", "none"))
            seen.add(payload)

        # Round 1: shuffle techniques and collect variants
        technique_order = list(self.techniques)
        random.shuffle(technique_order)

        for technique in technique_order:
            if len(results) >= target:
                break
            try:
                variants = technique.obfuscate(payload)
            except Exception as e:
                logger.warning("Technique %s failed on payload: %s", technique.name, e)
                continue
            for v in variants:
                if v not in seen:
                    seen.add(v)
                    results.append((payload, v, technique.name, technique.category))
                    if len(results) >= target:
                        break

        # Round 2: retry random techniques for stochastic variety
        max_retries = target * 3
        attempt = 0
        while len(results) < target and attempt < max_retries:
            technique = random.choice(self.techniques)
            attempt += 1
            try:
                variants = technique.obfuscate(payload)
            except Exception:
                continue
            for v in variants:
                if v not in seen:
                    seen.add(v)
                    results.append((payload, v, technique.name, technique.category))
                    if len(results) >= target:
                        break

        if len(results) < target:
            logger.warning(
                "Could only generate %d/%d unique variants for payload: %.40s...",
                len(results), target, payload,
            )

        return results

    def process_stream(
        self, payloads: Iterator[str]
    ) -> Iterator[Tuple[str, str, str, str]]:
        """Process an iterator of payloads, yielding result tuples."""
        for payload in payloads:
            for result in self.process_payload(payload):
                yield result
