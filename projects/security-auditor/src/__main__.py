"""Package entry point for ``python -m src``."""

from .audit import main

if __name__ == "__main__":
    raise SystemExit(main())
