#!/usr/bin/env python3
"""Generate a GitHub repositories fork/audit report for a user."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://api.github.com"


def _request_json(url: str, token: str | None = None) -> list[dict]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"******")

    with urllib.request.urlopen(req) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def fetch_repositories(username: str, token: str | None) -> list[dict]:
    repos: list[dict] = []
    page = 1
    per_page = 100

    while True:
        if token:
            params = urllib.parse.urlencode(
                {
                    "visibility": "all",
                    "affiliation": "owner",
                    "sort": "updated",
                    "per_page": per_page,
                    "page": page,
                }
            )
            url = f"{API_BASE}/user/repos?{params}"
            data = _request_json(url, token)
            page_items = [repo for repo in data if repo.get("owner", {}).get("login") == username]
        else:
            params = urllib.parse.urlencode(
                {
                    "type": "owner",
                    "sort": "updated",
                    "per_page": per_page,
                    "page": page,
                }
            )
            url = f"{API_BASE}/users/{username}/repos?{params}"
            page_items = _request_json(url)

        if not page_items:
            break

        repos.extend(page_items)
        if len(page_items) < per_page:
            break
        page += 1

    return repos


def repo_row(repo: dict) -> dict:
    parent = (repo.get("parent") or {}).get("full_name", "")
    source = (repo.get("source") or {}).get("full_name", "")
    visibility = "private" if repo.get("private") else "public"

    return {
        "name_with_owner": repo.get("full_name", ""),
        "name": repo.get("name", ""),
        "visibility": visibility,
        "is_fork": repo.get("fork", False),
        "parent": parent,
        "source": source,
        "archived": repo.get("archived", False),
        "default_branch": repo.get("default_branch", ""),
        "created_at": repo.get("created_at", ""),
        "updated_at": repo.get("updated_at", ""),
        "html_url": repo.get("html_url", ""),
    }


def write_csv(rows: list[dict], csv_path: Path) -> None:
    fields = [
        "name_with_owner",
        "name",
        "visibility",
        "is_fork",
        "parent",
        "source",
        "archived",
        "default_branch",
        "created_at",
        "updated_at",
        "html_url",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    rows: list[dict],
    md_path: Path,
    csv_path: Path,
    username: str,
    include_private: bool,
) -> None:
    total = len(rows)
    public_count = sum(1 for r in rows if r["visibility"] == "public")
    private_count = sum(1 for r in rows if r["visibility"] == "private")
    fork_count = sum(1 for r in rows if r["is_fork"])
    detached_candidates = [r for r in rows if not r["is_fork"] and r["visibility"] == "public"]

    lines = [
        "# GitHub Fork Audit Report",
        "",
        f"- **User:** `{username}`",
        f"- **Generated at (UTC):** `{dt.datetime.now(dt.UTC).isoformat()}`",
        f"- **Source scope:** {'All owner repos (public + private, token used)' if include_private else 'Public owner repos only (no token provided)'}",
        f"- **CSV file:** `{csv_path.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Total repos scanned: **{total}**",
        f"- Public repos: **{public_count}**",
        f"- Private repos: **{private_count}**",
        f"- Official GitHub forks (`is_fork=true`): **{fork_count}**",
        f"- Public repos with no fork link (`is_fork=false`): **{len(detached_candidates)}**",
        "",
        "## Important note",
        "",
        "If a repository was detached from its original fork network, GitHub API usually returns `is_fork=false` and no `parent/source`.",
        "So detached forks cannot be proven automatically from API metadata alone; they are only **candidates** for manual review.",
        "",
        "## Official forks found",
        "",
    ]

    official = [r for r in rows if r["is_fork"]]
    if official:
        lines.extend([
            "| Repository | Visibility | Parent | Source |",
            "|---|---|---|---|",
        ])
        for r in sorted(official, key=lambda x: x["name_with_owner"].lower()):
            lines.append(
                f"| `{r['name_with_owner']}` | `{r['visibility']}` | `{r['parent'] or '-'}` | `{r['source'] or '-'}` |"
            )
    else:
        lines.append("No official forks were returned by GitHub metadata.")

    lines.extend([
        "",
        "## Public repos to review manually (possible detached forks)",
        "",
        "| Repository | Updated | URL |",
        "|---|---|---|",
    ])

    for r in sorted(detached_candidates, key=lambda x: x["updated_at"], reverse=True):
        lines.append(
            f"| `{r['name_with_owner']}` | `{r['updated_at']}` | {r['html_url']} |"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate GitHub fork/public audit report.")
    parser.add_argument("--username", required=True, help="GitHub username to audit")
    parser.add_argument(
        "--output-dir",
        default="docs/reports",
        help="Directory where CSV and Markdown report files will be written",
    )
    parser.add_argument(
        "--report-prefix",
        default="github_fork_audit",
        help="Filename prefix for generated files",
    )
    parser.add_argument(
        "--input-json",
        help=(
            "Optional path to a JSON file containing GitHub repository data. "
            "Supported formats: {'items': [...]} from search API or a direct list."
        ),
    )
    args = parser.parse_args()

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.input_json:
        raw = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("items"), list):
            repos_data = raw["items"]
        elif isinstance(raw, list):
            repos_data = raw
        else:
            raise ValueError("Unsupported JSON input format for --input-json")
    else:
        repos_data = fetch_repositories(args.username, token)

    rows = [repo_row(repo) for repo in repos_data]
    rows.sort(key=lambda x: x["name_with_owner"].lower())

    csv_path = output_dir / f"{args.report_prefix}.csv"
    md_path = output_dir / f"{args.report_prefix}.md"

    write_csv(rows, csv_path)
    write_markdown(rows, md_path, csv_path, args.username, include_private=bool(token))

    print(f"Generated: {csv_path}")
    print(f"Generated: {md_path}")
    print(f"Repositories scanned: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
