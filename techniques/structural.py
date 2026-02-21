"""Structural obfuscation techniques."""

import base64
import random
import urllib.parse
from typing import List

from techniques.base import BaseTechnique, register


@register
class StringConcatenation(BaseTechnique):
    name = "string_concat"
    category = "structural"

    def obfuscate(self, payload: str) -> List[str]:
        if len(payload) < 2:
            return []
        results = []
        for _ in range(2):
            split = random.randint(1, len(payload) - 1)
            results.append(f'"{payload[:split]}" + "{payload[split:]}"')
        # Multi-split variant
        parts = [payload[i:i + 3] for i in range(0, len(payload), 3)]
        results.append(" + ".join(f'"{p}"' for p in parts))
        return results


@register
class CommentInjection(BaseTechnique):
    name = "comment_inject"
    category = "structural"

    def obfuscate(self, payload: str) -> List[str]:
        if len(payload) < 2:
            return []
        mid = len(payload) // 2
        return [
            f"{payload[:mid]}/**/{payload[mid:]}",
            f"{payload[:mid]}<!-- -->{payload[mid:]}",
        ]


@register
class EncodingChain(BaseTechnique):
    name = "encoding_chain"
    category = "structural"

    def obfuscate(self, payload: str) -> List[str]:
        # base64 then URL-encode
        b64 = base64.b64encode(payload.encode()).decode()
        chained = urllib.parse.quote(b64, safe="")
        return [chained]
