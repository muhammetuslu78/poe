"""Tests for POE - Payload Obfuscation Engine."""

import json
import os
import sys
import tempfile
import time
import unittest

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import validate_multiplier, validate_format, validate_file_readable
from techniques.base import get_all_techniques, get_technique_by_name, get_techniques_by_category
import techniques  # triggers registration
from core.engine import ObfuscationEngine
from core.input_handler import read_payloads
from core.output_handler import write_text, write_json


class TestValidators(unittest.TestCase):
    def test_valid_multiplier(self):
        self.assertEqual(validate_multiplier(5), 5)
        self.assertEqual(validate_multiplier(1), 1)
        self.assertEqual(validate_multiplier(20), 20)

    def test_invalid_multiplier(self):
        with self.assertRaises(ValueError):
            validate_multiplier(0)
        with self.assertRaises(ValueError):
            validate_multiplier(21)
        with self.assertRaises(ValueError):
            validate_multiplier(-1)

    def test_valid_format(self):
        self.assertEqual(validate_format("text"), "text")
        self.assertEqual(validate_format("json"), "json")
        self.assertEqual(validate_format("JSON"), "json")

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            validate_format("xml")

    def test_file_readable_nonexistent(self):
        with self.assertRaises(ValueError):
            validate_file_readable("/nonexistent/file.txt")


class TestTechniqueRegistry(unittest.TestCase):
    def test_all_techniques_registered(self):
        techniques = get_all_techniques()
        self.assertGreaterEqual(len(techniques), 19)

    def test_get_by_name(self):
        t = get_technique_by_name("base64")
        self.assertEqual(t.name, "base64")
        self.assertEqual(t.category, "encoding")

    def test_get_by_invalid_name(self):
        with self.assertRaises(KeyError):
            get_technique_by_name("nonexistent_technique")

    def test_get_by_category(self):
        enc = get_techniques_by_category("encoding")
        self.assertGreaterEqual(len(enc), 6)
        for t in enc:
            self.assertEqual(t.category, "encoding")

    def test_all_techniques_have_required_attrs(self):
        for name, t in get_all_techniques().items():
            self.assertIsInstance(t.name, str)
            self.assertIsInstance(t.category, str)
            self.assertTrue(callable(t.obfuscate))


class TestEncodingTechniques(unittest.TestCase):
    PAYLOAD = "<script>alert('xss')</script>"

    def test_base64(self):
        t = get_technique_by_name("base64")
        results = t.obfuscate(self.PAYLOAD)
        self.assertGreaterEqual(len(results), 1)
        import base64
        self.assertEqual(base64.b64decode(results[0]).decode(), self.PAYLOAD)

    def test_url_encode(self):
        t = get_technique_by_name("url_encode")
        results = t.obfuscate(self.PAYLOAD)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("%3C", results[0])

    def test_html_entity_decimal(self):
        t = get_technique_by_name("html_entity_decimal")
        results = t.obfuscate("A")
        self.assertEqual(results, ["&#65;"])

    def test_html_entity_hex(self):
        t = get_technique_by_name("html_entity_hex")
        results = t.obfuscate("A")
        self.assertEqual(results, ["&#x41;"])

    def test_unicode_escape(self):
        t = get_technique_by_name("unicode_escape")
        results = t.obfuscate("A")
        self.assertEqual(results, ["\\u0041"])

    def test_hex_encode(self):
        t = get_technique_by_name("hex_encode")
        results = t.obfuscate("AB")
        self.assertIn("4142", results)


class TestMutationTechniques(unittest.TestCase):
    PAYLOAD = "<script>alert(1)</script>"

    def test_random_case(self):
        t = get_technique_by_name("random_case")
        results = t.obfuscate(self.PAYLOAD)
        self.assertGreaterEqual(len(results), 1)
        for r in results:
            self.assertEqual(r.lower(), self.PAYLOAD.lower())

    def test_alternating_case(self):
        t = get_technique_by_name("alternating_case")
        results = t.obfuscate(self.PAYLOAD)
        self.assertGreaterEqual(len(results), 1)

    def test_homoglyph(self):
        t = get_technique_by_name("homoglyph")
        results = t.obfuscate("script")
        self.assertEqual(len(results), 1)
        self.assertNotEqual(results[0], "script")
        self.assertEqual(len(results[0]), len("script"))

    def test_zero_width(self):
        t = get_technique_by_name("zero_width")
        results = t.obfuscate("abc")
        self.assertEqual(len(results), 1)
        self.assertIn('\u200b', results[0])


class TestStructuralTechniques(unittest.TestCase):
    def test_string_concat(self):
        t = get_technique_by_name("string_concat")
        results = t.obfuscate("hello world")
        self.assertGreaterEqual(len(results), 2)
        for r in results:
            self.assertIn("+", r)

    def test_string_concat_short(self):
        t = get_technique_by_name("string_concat")
        self.assertEqual(t.obfuscate("a"), [])

    def test_comment_inject(self):
        t = get_technique_by_name("comment_inject")
        results = t.obfuscate("SELECT * FROM users")
        self.assertEqual(len(results), 2)
        self.assertIn("/**/", results[0])

    def test_encoding_chain(self):
        t = get_technique_by_name("encoding_chain")
        results = t.obfuscate("test")
        self.assertEqual(len(results), 1)


class TestContextTechniques(unittest.TestCase):
    def test_js_template_literal(self):
        t = get_technique_by_name("js_template_literal")
        results = t.obfuscate("alert(1)")
        self.assertEqual(results, ["`alert(1)`"])

    def test_js_eval_wrap(self):
        t = get_technique_by_name("js_eval_wrap")
        results = t.obfuscate("alert(1)")
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].startswith("eval("))

    def test_sql_comment_inject(self):
        t = get_technique_by_name("sql_comment_inject")
        results = t.obfuscate("SELECT * FROM users")
        self.assertEqual(len(results), 1)
        self.assertIn("/**/", results[0])

    def test_sql_keyword_split(self):
        t = get_technique_by_name("sql_keyword_split")
        results = t.obfuscate("SELECT * FROM users")
        self.assertEqual(len(results), 1)
        self.assertIn("/**/", results[0])

    def test_html_attr_variation(self):
        t = get_technique_by_name("html_attr_variation")
        results = t.obfuscate("<img src='x' onerror='alert(1)'>")
        self.assertGreaterEqual(len(results), 1)

    def test_html_tag_mutation(self):
        t = get_technique_by_name("html_tag_mutation")
        results = t.obfuscate("<script>alert(1)</script>")
        self.assertEqual(len(results), 2)

    def test_html_tag_mutation_no_html(self):
        t = get_technique_by_name("html_tag_mutation")
        self.assertEqual(t.obfuscate("no tags here"), [])


class TestEngine(unittest.TestCase):
    def test_multiplier_met(self):
        engine = ObfuscationEngine(multiplier=5)
        results = engine.process_payload("<script>alert('xss')</script>")
        self.assertEqual(len(results), 5)

    def test_deduplication(self):
        engine = ObfuscationEngine(multiplier=10)
        results = engine.process_payload("<script>alert(1)</script>")
        obfuscated = [r[1] for r in results]
        self.assertEqual(len(obfuscated), len(set(obfuscated)))

    def test_preserve_original(self):
        engine = ObfuscationEngine(multiplier=3, preserve_original=True)
        results = engine.process_payload("test payload")
        originals = [r for r in results if r[2] == "original"]
        self.assertEqual(len(originals), 1)
        self.assertEqual(originals[0][1], "test payload")

    def test_technique_filter(self):
        engine = ObfuscationEngine(multiplier=2, technique_names=["base64", "hex_encode"])
        results = engine.process_payload("test")
        for r in results:
            self.assertIn(r[2], ("base64", "hex_encode"))

    def test_short_payload_graceful(self):
        engine = ObfuscationEngine(multiplier=5)
        results = engine.process_payload("a")
        self.assertGreater(len(results), 0)

    def test_stream_processing(self):
        engine = ObfuscationEngine(multiplier=2)
        payloads = iter(["payload1", "payload2"])
        results = list(engine.process_stream(payloads))
        self.assertEqual(len(results), 4)


class TestInputHandler(unittest.TestCase):
    def test_read_payloads(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("payload1\n# comment\n\npayload2\n")
            f.flush()
            path = f.name
        try:
            payloads = list(read_payloads(path))
            self.assertEqual(payloads, ["payload1", "payload2"])
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        with self.assertRaises(ValueError):
            list(read_payloads("/nonexistent/file.txt"))


class TestOutputHandler(unittest.TestCase):
    def test_text_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            path = f.name
        try:
            data = iter([("orig", "obf1", "base64", "encoding"), ("orig", "obf2", "hex", "encoding")])
            write_text(data, path)
            with open(path, "r") as f:
                lines = f.read().strip().split("\n")
            self.assertEqual(lines, ["obf1", "obf2"])
        finally:
            os.unlink(path)

    def test_json_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            data = iter([("orig", "obf1", "base64", "encoding")])
            write_json(data, path)
            with open(path, "r") as f:
                parsed = json.load(f)
            self.assertEqual(len(parsed), 1)
            self.assertEqual(parsed[0]["original"], "orig")
            self.assertEqual(parsed[0]["obfuscated"], "obf1")
            self.assertEqual(parsed[0]["technique"], "base64")
            self.assertIn("timestamp", parsed[0])
        finally:
            os.unlink(path)


class TestPerformance(unittest.TestCase):
    def test_100_payloads_under_5_seconds(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            for i in range(100):
                f.write(f"<script>alert({i})</script>\n")
            path = f.name
        try:
            engine = ObfuscationEngine(multiplier=5)
            start = time.monotonic()
            payloads = read_payloads(path)
            results = list(engine.process_stream(payloads))
            elapsed = time.monotonic() - start
            self.assertGreaterEqual(len(results), 400)
            self.assertLess(elapsed, 5.0, f"Took {elapsed:.2f}s, expected < 5s")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
