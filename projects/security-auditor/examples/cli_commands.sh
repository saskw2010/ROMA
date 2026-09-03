#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python src/audit.py --repo https://github.com/example/repo --branch main
python src/audit.py --help
