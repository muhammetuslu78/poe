"""Character mutation obfuscation techniques."""

import random
from typing import List

from techniques.base import BaseTechnique, register


@register
class RandomCase(BaseTechnique):
    name = "random_case"
    category = "mutation"

    def obfuscate(self, payload: str) -> List[str]:
        results = []
        for _ in range(3):
            variant = "".join(
                c.upper() if random.random() > 0.5 else c.lower()
                for c in payload
            )
            if variant != payload:
                results.append(variant)
        return results


@register
class AlternatingCase(BaseTechnique):
    name = "alternating_case"
    category = "mutation"

    def obfuscate(self, payload: str) -> List[str]:
        v1 = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload))
        v2 = "".join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(payload))
        results = []
        if v1 != payload:
            results.append(v1)
        if v2 != payload and v2 != v1:
            results.append(v2)
        return results


@register
class HomoglyphSubstitution(BaseTechnique):
    name = "homoglyph"
    category = "mutation"

    HOMOGLYPHS = {
        'a': '\u0430', 'e': '\u0435', 'o': '\u043e', 'p': '\u0440',
        'c': '\u0441', 'x': '\u0445', 's': '\u0455', 'i': '\u0456',
        'A': '\u0410', 'B': '\u0412', 'E': '\u0415', 'H': '\u041d',
        'K': '\u041a', 'M': '\u041c', 'O': '\u041e', 'P': '\u0420',
        'T': '\u0422', 'X': '\u0425', 'S': '\u0405', 'C': '\u0421',
    }

    def obfuscate(self, payload: str) -> List[str]:
        full = "".join(self.HOMOGLYPHS.get(c, c) for c in payload)
        if full == payload:
            return []
        return [full]


@register
class ZeroWidthInsertion(BaseTechnique):
    name = "zero_width"
    category = "mutation"

    ZWSP = '\u200b'

    def obfuscate(self, payload: str) -> List[str]:
        return [self.ZWSP.join(payload)]
