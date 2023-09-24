"""
Script to filter GitHub issues based on tags, showing only help-wanted issues.

Author: GPT-4

Usage:
  python get_help_wanted.py <input.csv> --output <output.csv> [--good-first-issue] [--accepting-prs]
"""

import argparse
import csv
import sys
from typing import List, Dict

# Increase CSV field size limit
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

GOOD_FIRST_ISSUE_LABELS = list(
    map(
        lambda x: x.lower(),
        [
            "good first issue",
            "good-first-issue",
            "first-timers-only",
            "beginner-friendly",
            "starter issue",
            "documentation" "easy bug fix",
            "low-hanging-fruit",
            "easy",
            "beginner",
            "first timer",
            "first-time-contributor",
            "starter",
            "up-for-grabs",
            "beginners-only",
            "beginner issue",
            "newbie",
            "E-easy",
            "difficulty: easy",
            "starter bug",
            "good for beginner",
            "good 4 newbie",
        ],
    )
)

ACCEPTING_PRS_LABELS = list(
    map(
        lambda x: x.lower(),
        [
            "accepting prs",
            "pr welcome",
            "pr-welcome",
            "pr wanted",
            "pr-wanted",
            "hacktoberfest",
            "open for pr",
            "pull request welcome",
            "pull requests welcome",
            "PRs accepted",
            "pr needed",
            "pr's welcome",
            "pull-request-welcome",
            "pull-requests-accepted",
            "pull-request-accepted",
            "contribution welcome",
            "contributions welcome",
            "open for pull requests",
            "pr open",
            "prs open",
            "pulls welcome",
            "good second issue",
        ],
    )
)

NOT_OPEN_LABELS = list(
    map(
        lambda x: x.lower(),
        [
            "wontfix",
            "invalid",
            "duplicate",
            "on hold",
            "waiting-for",
            "stale",
            "blocked",
            "under investigation",
            "cannot reproduce",
            "needs info",
            "needs investigation",
            "needs triage",
            "needs-repro",
            "unreproducible",
            "discussion",
            "question",
            "support",
            "on-hold",
            "needs-more-info",
            "declined",
            "not-a-bug",
            "not reproducible",
            "can't reproduce",
            "wont-fix",
            "invalid-issue",
            "to-be-closed",
            "incomplete",
            "in-progress",
            "needs-discussion",
            "awaiting-feedback",
            "more-information-needed",
        ],
    )
)


def issue_filter(
    issue: Dict[str, str], good_first_issues: bool, accepting_prs: bool
) -> bool:
    labels = issue["Labels"].lower().split(", ")
    labels += list(map(lambda x: x.replace(" ", "-"), labels))
    labels += list(map(lambda x: x.replace("-", " "), labels))
    # Always filter out NOT_OPEN_LABELS
    if any(label in NOT_OPEN_LABELS for label in labels):
        return False
    if any(
        "waiting" in label
        or "blocked" in label
        or "linear" in label
        or "discuss" in label
        for label in labels
    ):
        return False
    if (good_first_issues or accepting_prs) and any(
        "easy" in label or "beginner" in label for label in labels
    ):
        return True
    if (good_first_issues or accepting_prs) and any(
        label in GOOD_FIRST_ISSUE_LABELS for label in labels
    ):
        return True
    if good_first_issues:
        return False
    if accepting_prs and any(
        "help" in label or "accepting" in label or "contrib" in label
        for label in labels
    ):
        return True
    if accepting_prs and any(label in ACCEPTING_PRS_LABELS for label in labels):
        return True
    if accepting_prs:
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input CSV file")
    parser.add_argument("--output", type=str, required=True, help="Output CSV file")
    parser.add_argument(
        "--good-first-issue", action="store_true", help="Include only good first issues"
    )
    parser.add_argument(
        "--accepting-prs", action="store_true", help="Include only issues accepting PRs"
    )
    parser.add_argument(
        "--encoding", type=str, default = "utf8", help="The encoding of the CSV file"
    )
    args = parser.parse_args()

    with (open(args.input, "r", encoding = args.encoding) as f_in, 
          open(args.output, "w", newline="", encoding = args.encoding) as f_out):
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        writer.writeheader()
        for issue in reader:
            if issue_filter(issue, args.good_first_issue, args.accepting_prs):
                writer.writerow(issue)


if __name__ == "__main__":
    main()
