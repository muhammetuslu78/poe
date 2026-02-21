"""Encoding-based obfuscation techniques."""

import base64
import urllib.parse
from typing import List

from techniques.base import BaseTechnique, register


@register
class Base64Encode(BaseTechnique):
    name = "base64"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        standard = base64.b64encode(payload.encode()).decode()
        urlsafe = base64.urlsafe_b64encode(payload.encode()).decode()
        results = [standard]
        if urlsafe != standard:
            results.append(urlsafe)
        return results


@register
class UrlEncode(BaseTechnique):
    name = "url_encode"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        full = urllib.parse.quote(payload, safe="")
        partial = urllib.parse.quote(payload)
        results = [full]
        if partial != full:
            results.append(partial)
        return results


@register
class HtmlEntityDecimal(BaseTechnique):
    name = "html_entity_decimal"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        return ["".join(f"&#{ord(c)};" for c in payload)]


@register
class HtmlEntityHex(BaseTechnique):
    name = "html_entity_hex"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        return ["".join(f"&#x{ord(c):x};" for c in payload)]


@register
class UnicodeEscape(BaseTechnique):
    name = "unicode_escape"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        short = "".join(f"\\u{ord(c):04x}" for c in payload)
        return [short]


@register
class HexEncode(BaseTechnique):
    name = "hex_encode"
    category = "encoding"

    def obfuscate(self, payload: str) -> List[str]:
        plain = payload.encode().hex()
        prefixed = "".join(f"\\x{b:02x}" for b in payload.encode())
        return [plain, prefixed]
