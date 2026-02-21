<div align="center">

```
██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝
██████╔╝██║   ██║█████╗
██╔═══╝ ██║   ██║██╔══╝
██║     ╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚══════╝
```

# Payload Obfuscation Engine

**Transform security payloads into hundreds of obfuscated variants in milliseconds.**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen?style=for-the-badge)](#requirements)
[![Tests: 42 Passing](https://img.shields.io/badge/Tests-42%20Passing-success?style=for-the-badge)](#testing)

---

*A high-performance, modular CLI tool that takes a handful of base payloads and expands them into a rich corpus of obfuscated variants — purpose-built for authorized penetration testing, red team operations, and security research.*

[Quick Start](#quick-start) · [Techniques](#obfuscation-techniques) · [Usage](#usage) · [Architecture](#architecture) · [Contributing](#contributing)

</div>

---

## Why POE?

Modern web application firewalls (WAFs) and intrusion detection systems rely on signature-based pattern matching to block known attack vectors. A single payload written one way will be caught — but the same payload expressed through different encodings, case mutations, or structural transformations can reveal gaps in defensive coverage.

**POE automates this expansion.** Feed it 100 base payloads and get back 500+ unique, semantically equivalent variants — each crafted through a different obfuscation strategy.

### Key Highlights

| | Feature | Description |
|---|---|---|
| ⚡ | **Blazing Fast** | Processes 1,000+ payloads per second with streaming I/O |
| 🧩 | **19 Techniques** | Encoding, mutation, structural, and context-aware obfuscation |
| 📦 | **Zero Dependencies** | Pure Python standard library — no `pip install` required |
| 🔄 | **Streaming Pipeline** | Constant memory usage regardless of input size |
| 🎯 | **Configurable** | Choose specific techniques, set multiplier (1–20x), pick output format |
| 🏗️ | **Modular Architecture** | Add new techniques with a single decorated class |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/muhammetuslu78/poe.git
cd poe

# Run with the included sample payloads
python3 poe.py -i sample_payloads.txt -o results.txt

# Generate 10 variants per payload in JSON format
python3 poe.py -i sample_payloads.txt -o results.json -f json -m 10

# Use only specific techniques
python3 poe.py -i sample_payloads.txt -o results.txt -t base64 url_encode homoglyph

# Pipe directly to another tool
python3 poe.py -i payloads.txt -m 3 | httpx -silent
```

### Input Format

Create a text file with one payload per line. Lines starting with `#` are treated as comments, and empty lines are skipped:

```text
# XSS Vectors
<script>alert('xss')</script>
<img src=x onerror=alert(1)>

# SQL Injection
' OR 1=1 --
' UNION SELECT NULL,NULL--
```

---

## Obfuscation Techniques

POE ships with **19 built-in techniques** organized into four categories. Each technique is independently selectable via the `-t` flag.

### Encoding (6 techniques)

Transform payload characters into equivalent encoded representations that bypass string-matching filters.

| Technique | ID | Example Input | Example Output |
|---|---|---|---|
| **Base64** | `base64` | `<script>alert(1)</script>` | `PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==` |
| **URL Encode** | `url_encode` | `<script>alert(1)</script>` | `%3Cscript%3Ealert%281%29%3C%2Fscript%3E` |
| **HTML Entity (Decimal)** | `html_entity_decimal` | `<A>` | `&#60;&#65;&#62;` |
| **HTML Entity (Hex)** | `html_entity_hex` | `<A>` | `&#x3c;&#x41;&#x3e;` |
| **Unicode Escape** | `unicode_escape` | `alert` | `\u0061\u006c\u0065\u0072\u0074` |
| **Hex Encode** | `hex_encode` | `AB` | `4142` / `\x41\x42` |

### Mutation (4 techniques)

Alter individual characters while preserving visual or functional equivalence.

| Technique | ID | Example Input | Example Output |
|---|---|---|---|
| **Random Case** | `random_case` | `<script>` | `<sCrIpT>` |
| **Alternating Case** | `alternating_case` | `<script>` | `<ScRiPt>` |
| **Homoglyph Substitution** | `homoglyph` | `script` | `ѕсrірt` *(Cyrillic lookalikes)* |
| **Zero-Width Insertion** | `zero_width` | `alert` | `a​l​e​r​t` *(invisible chars between)* |

### Structural (3 techniques)

Modify the payload's structure without changing its meaning.

| Technique | ID | Example Input | Example Output |
|---|---|---|---|
| **String Concatenation** | `string_concat` | `alert('xss')` | `"ale" + "rt(" + "'xs" + "s')"` |
| **Comment Injection** | `comment_inject` | `SELECT * FROM` | `SELECT/**/ * FROM` |
| **Encoding Chain** | `encoding_chain` | `test` | `dGVzdA%3D%3D` *(Base64 → URL)* |

### Context-Aware (6 techniques)

Apply transformations specific to JavaScript, SQL, or HTML contexts.

| Technique | ID | Context | Example Output |
|---|---|---|---|
| **JS Template Literal** | `js_template_literal` | JavaScript | `` `alert(1)` `` |
| **JS Eval Wrap** | `js_eval_wrap` | JavaScript | `eval(String.fromCharCode(97,108,...))` |
| **SQL Comment Inject** | `sql_comment_inject` | SQL | `SELECT/**/username/**/FROM/**/users` |
| **SQL Keyword Split** | `sql_keyword_split` | SQL | `SEL/**/ECT * FR/**/OM users` |
| **HTML Attribute Variation** | `html_attr_variation` | HTML | Quote swapping + tag uppercasing |
| **HTML Tag Mutation** | `html_tag_mutation` | HTML | `< script>` / `<script/>` |

---

## Usage

### Command-Line Interface

```
usage: poe [-h] -i INPUT [-o OUTPUT] [-m MULTIPLIER] [-f {text,json}]
           [-t TECHNIQUES [TECHNIQUES ...]] [-p] [-v]
```

### Arguments

| Argument | Short | Type | Default | Description |
|---|---|---|---|---|
| `--input` | `-i` | string | *required* | Input file path (one payload per line) |
| `--output` | `-o` | string | stdout | Output file path |
| `--multiplier` | `-m` | int | `5` | Number of variants per payload (1–20) |
| `--format` | `-f` | string | `text` | Output format: `text` or `json` |
| `--techniques` | `-t` | list | all | Space-separated technique IDs to use |
| `--preserve` | `-p` | flag | false | Include original payloads in output |
| `--verbose` | `-v` | flag | false | Enable detailed debug logging |

### Output Formats

**Text** — One obfuscated payload per line, ready to pipe into other tools:

```bash
python3 poe.py -i payloads.txt -m 5
```

```
%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E
PHNjcmlwdD5hbGVydCgneHNzJyk8L3NjcmlwdD4=
<ScRiPt>alert('xss')</ScRiPt>
...
```

**JSON** — Rich metadata for each variant, ideal for integration and analysis:

```bash
python3 poe.py -i payloads.txt -f json -m 3 -o results.json
```

```json
[
  {
    "original": "<script>alert('xss')</script>",
    "obfuscated": "%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E",
    "technique": "url_encode",
    "technique_category": "encoding",
    "timestamp": "2026-02-21T13:00:00.000000+00:00"
  }
]
```

### Practical Examples

```bash
# WAF bypass testing — generate heavy obfuscation with all techniques
python3 poe.py -i xss_payloads.txt -o waf_test.txt -m 15

# SQL injection focused — only SQL-relevant techniques
python3 poe.py -i sqli.txt -o sqli_obfuscated.txt -t url_encode sql_comment_inject sql_keyword_split encoding_chain

# Encoding-only variants for filter testing
python3 poe.py -i payloads.txt -o encoded.txt -t base64 url_encode hex_encode html_entity_decimal html_entity_hex unicode_escape

# Keep originals alongside variants for A/B comparison
python3 poe.py -i payloads.txt -o compared.json -f json -m 3 -p

# Pipeline with other security tools
python3 poe.py -i payloads.txt -m 5 | nuclei -t xss-detection.yaml
python3 poe.py -i payloads.txt -m 3 | ffuf -u "https://target.com/search?q=FUZZ" -w -
```

---

## Architecture

```
poe/
├── poe.py                    # CLI entry point — argparse, pipeline wiring
├── core/
│   ├── engine.py             # Orchestrator — technique selection, dedup, multiplier
│   ├── input_handler.py      # Streaming file reader with comment/blank filtering
│   └── output_handler.py     # Text and JSON streaming writers
├── techniques/
│   ├── base.py               # BaseTechnique ABC + @register decorator registry
│   ├── encoding.py           # 6 encoding technique classes
│   ├── mutation.py           # 4 character mutation classes
│   ├── structural.py         # 3 structural transformation classes
│   └── context.py            # 6 context-aware technique classes
├── utils/
│   └── validators.py         # Input validation functions
├── tests/
│   └── test_engine.py        # 42-test comprehensive suite
└── sample_payloads.txt       # Example payload collection
```

### Design Principles

**Streaming Pipeline** — The entire data flow from file reading through obfuscation to output writing is lazy. Generators pass data one payload at a time, ensuring constant memory usage whether processing 10 payloads or 10 million.

```
read_payloads() ──▶ engine.process_stream() ──▶ write_text() / write_json()
   Iterator[str]       Iterator[Tuple]              File / stdout
```

**Self-Registering Techniques** — Each technique class is decorated with `@register`, which automatically adds it to a global registry at import time. Adding a new technique requires zero wiring — just define the class:

```python
from techniques.base import BaseTechnique, register

@register
class MyTechnique(BaseTechnique):
    name = "my_technique"
    category = "encoding"

    def obfuscate(self, payload: str) -> list:
        return [payload.upper()]  # your logic here
```

**Two-Round Multiplier Strategy** — The engine uses a deterministic first pass (shuffled technique sweep) followed by a stochastic second pass (random retries on techniques that produce non-deterministic output like `random_case`) to reliably hit the target multiplier while maximizing variant diversity.

---

## Requirements

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- **No external dependencies** — uses only the Python standard library

---

## Testing

POE includes a comprehensive test suite with 42 tests covering every layer:

```bash
# Run all tests
python3 -m unittest tests/test_engine.py -v

# Run a specific test class
python3 -m unittest tests.test_engine.TestEngine -v

# Run a single test
python3 -m unittest tests.test_engine.TestEncodingTechniques.test_base64 -v
```

### Test Coverage

| Test Class | Tests | Covers |
|---|---|---|
| `TestValidators` | 5 | Input validation edge cases |
| `TestTechniqueRegistry` | 5 | Technique discovery and lookup |
| `TestEncodingTechniques` | 6 | All 6 encoding techniques with known outputs |
| `TestMutationTechniques` | 4 | Case, homoglyph, and zero-width mutations |
| `TestStructuralTechniques` | 4 | Concatenation, comments, chaining |
| `TestContextTechniques` | 7 | JS, SQL, and HTML context-aware transforms |
| `TestEngine` | 6 | Multiplier, dedup, filtering, streaming |
| `TestInputHandler` | 2 | File reading, comment skipping |
| `TestOutputHandler` | 2 | Text and JSON output formatting |
| `TestPerformance` | 1 | 100 payloads × 5x under 5 seconds |

---

## Performance

| Metric | Value |
|---|---|
| Throughput | **1,000+ payloads/second** |
| 100 payloads × 5x multiplier | **< 0.01 seconds** |
| Memory usage | **Constant** (streaming) |
| Startup time | **< 50ms** |

---

## Roadmap

- [ ] Payload type auto-detection (XSS, SQLi, CMDi)
- [ ] Custom technique plugin system (load from external `.py` files)
- [ ] Deobfuscation / reverse mode
- [ ] Payload effectiveness scoring with ML
- [ ] Integration with Burp Suite / OWASP ZAP
- [ ] Payload length constraints and budget mode
- [ ] YAML/TOML configuration files
- [ ] Docker image for CI/CD pipelines

---

## Legal Disclaimer

> **This tool is provided for authorized security testing, penetration testing, and educational research purposes only.** The authors assume no liability for misuse of this software. Users are solely responsible for ensuring they have proper authorization before using POE against any target system. Unauthorized use of this tool against systems you do not own or have explicit permission to test is illegal and unethical.

---

## Contributing

Contributions are welcome! To add a new obfuscation technique:

1. Choose the appropriate module (`encoding.py`, `mutation.py`, `structural.py`, or `context.py`)
2. Create a class extending `BaseTechnique` with the `@register` decorator
3. Implement `name`, `category`, and `obfuscate()` — return a `list` of variants
4. Add corresponding tests in `tests/test_engine.py`
5. Submit a pull request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for security professionals, by security professionals.**

*If POE helped your security testing workflow, consider giving it a ⭐*

</div>
