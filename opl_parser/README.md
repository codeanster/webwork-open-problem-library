# OPL Parser

Tools for extracting structured representations of WeBWorK Open Problem Library (OPL) PG files. The package
provides a modular parsing pipeline, command-line entry points, and serializers for exporting the resulting
problem metadata.

## Features

- Metadata extraction from the canonical `## DBsubject(...)` headers.
- Normalized student-facing text assembled from classic `BEGIN_TEXT` and PGML blocks.
- Variable and helper-logic capture for reproducibility.
- Answer evaluation modeling, including comparator types and grader configuration.
- Streaming JSONL export suitable for downstream analytics pipelines.

## Project Layout

```
opl_parser/
├── pyproject.toml
├── README.md
├── config/
│   └── parser.yaml
├── src/opl_parser/
│   ├── cli.py
│   ├── parser.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── metadata.py
│   │   ├── text.py
│   │   ├── variables.py
│   │   └── answers.py
│   └── serializers/
│       ├── __init__.py
│       ├── jsonl.py
│       └── schema.py
├── tests/
│   ├── conftest.py
│   ├── data/
│   ├── test_metadata.py
│   ├── test_text.py
│   ├── test_variables.py
│   └── test_answers.py
├── scripts/
│   └── run_parse.py
└── outputs/
    ├── samples/
    └── full/
```

## Quick Start

1. Install in editable mode:

   ```bash
   pip install -e .[dev]
   ```

2. Run the parser against a local OPL checkout:

   ```bash
   opl-parser parse --root data/raw/OpenProblemLibrary --output outputs/samples
   ```

3. Inspect JSONL results in `outputs/samples` before scaling up to full-library exports.

## Configuration

Runtime behavior is controlled by `config/parser.yaml`, which specifies default input roots, output
directories, and toggle flags. Override settings through CLI options or environment variables as needed.

## License

The parser is distributed under the same license as the WeBWorK Open Problem Library. See `../OPL_LICENSE`
for details.
