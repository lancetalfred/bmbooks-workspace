#!/usr/bin/env python3
"""One-time migration: create GitHub Issues from a curated JSON list.

Usage: python3 migrate_issues.py issues_pre_launch.json
Idempotent — skips any issue whose exact title already exists.
"""

import json
import subprocess
import sys


def existing_titles():
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "all", "--limit", "200", "--json", "title"],
        capture_output=True, text=True, check=True,
    )
    return {item["title"] for item in json.loads(result.stdout)}


def create_issue(item, known_titles):
    if item["title"] in known_titles:
        print(f"SKIP (exists): {item['title']}")
        return

    cmd = [
        "gh", "issue", "create",
        "--title", item["title"],
        "--body", item["body"],
        "--milestone", item["milestone"],
    ]
    for label in item["labels"]:
        cmd += ["--label", label]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"CREATED: {item['title']} -> {result.stdout.strip()}")
    else:
        print(f"FAILED: {item['title']} -> {result.stderr.strip()}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 migrate_issues.py <issues.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        items = json.load(f)

    known = existing_titles()
    for item in items:
        create_issue(item, known)


if __name__ == "__main__":
    main()
