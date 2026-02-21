"""Context-aware obfuscation techniques (JS, SQL, HTML)."""

import re
from typing import List

from techniques.base import BaseTechnique, register


@register
class JsTemplateLiteral(BaseTechnique):
    name = "js_template_literal"
    category = "context"

    def obfuscate(self, payload: str) -> List[str]:
        escaped = payload.replace("`", "\\`").replace("${", "\\${")
        return [f"`{escaped}`"]


@register
class JsEvalWrap(BaseTechnique):
    name = "js_eval_wrap"
    category = "context"

    def obfuscate(self, payload: str) -> List[str]:
        char_codes = ",".join(str(ord(c)) for c in payload)
        return [
            f'eval("{payload}")',
            f"eval(String.fromCharCode({char_codes}))",
        ]


@register
class SqlCommentInject(BaseTechnique):
    name = "sql_comment_inject"
    category = "context"

    def obfuscate(self, payload: str) -> List[str]:
        words = payload.split()
        if len(words) < 2:
            return []
        return ["/**/".join(words)]


@register
class SqlKeywordSplit(BaseTechnique):
    name = "sql_keyword_split"
    category = "context"

    SQL_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "AND", "OR", "UNION",
        "INSERT", "UPDATE", "DELETE", "DROP", "TABLE",
    }

    def obfuscate(self, payload: str) -> List[str]:
        words = payload.split()
        result = []
        for w in words:
            if w.upper() in self.SQL_KEYWORDS and len(w) > 2:
                mid = len(w) // 2
                result.append(f"{w[:mid]}/**/{w[mid:]}")
            else:
                result.append(w)
        joined = " ".join(result)
        return [joined] if joined != payload else []


@register
class HtmlAttributeVariation(BaseTechnique):
    name = "html_attr_variation"
    category = "context"

    def obfuscate(self, payload: str) -> List[str]:
        results = []
        if "'" in payload:
            results.append(payload.replace("'", '"'))
        if '"' in payload:
            results.append(payload.replace('"', "'"))
        if "<" in payload:
            results.append(re.sub(
                r'<(/?)(\w+)',
                lambda m: f"<{m.group(1)}{m.group(2).upper()}",
                payload,
            ))
        return results


@register
class HtmlTagMutation(BaseTechnique):
    name = "html_tag_mutation"
    category = "context"

    def obfuscate(self, payload: str) -> List[str]:
        if "<" not in payload:
            return []
        results = []
        results.append(re.sub(r'<(\w+)', r'< \1', payload))
        results.append(re.sub(r'<(\w+)', r'<\1/', payload))
        return results
