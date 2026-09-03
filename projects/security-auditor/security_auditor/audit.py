"""Compatibility wrapper for CLI entrypoint."""

from src.audit import build_parser, main, run_audit

__all__ = ["build_parser", "run_audit", "main"]
