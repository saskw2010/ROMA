"""Module entrypoint for `python -m security_auditor`."""

from .audit import main

if __name__ == "__main__":
    raise SystemExit(main())
