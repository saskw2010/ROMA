"""Module entrypoint for `python -m security_auditor` style execution."""

from .audit import main

if __name__ == "__main__":
    raise SystemExit(main())
