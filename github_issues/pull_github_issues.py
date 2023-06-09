"""
Script to pull open GitHub issues from all repositories the user has starred.

Author: GPT-4

Usage:
  python pull_github_issues.py --max_issues <max_issues> --days <days> --output <output.csv>
"""

import argparse
import csv
import requests
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API_TOKEN from environment variables
API_TOKEN = os.getenv("API_TOKEN")

# Increase CSV field size limit
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

# Setting up logging
logging.basicConfig(level=logging.INFO)

headers = {"Authorization": f"token {API_TOKEN}"}


def get_next_page_link(link_header: str) -> Optional[str]:
    if link_header:
        links = link_header.split(", ")
        for link in links:
            url, rel = link.split("; ")
            if rel == 'rel="next"':
                return url.strip("<>")
    return None


def get_starred_repos() -> List[str]:
    url = "https://api.github.com/user/starred?per_page=100"
    all_repos = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_repos.extend([repo["full_name"] for repo in response.json()])
        url = get_next_page_link(response.headers.get("Link", ""))
    return all_repos


def get_issues(repo_full_name: str, max_issues: int, days: int) -> List[dict]:
    cutoff_date = datetime.now() - timedelta(days=days)
    params = {
        "state": "open",
        "sort": "updated",
        "direction": "desc",
        "per_page": 100,
        "since": cutoff_date.isoformat(),
    }
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    all_issues = []
    while url and len(all_issues) < max_issues:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        for issue in response.json():
            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if "pull_request" in issue or created_at < cutoff_date or issue["assignee"]:
                continue
            all_issues.append(
                {
                    "Repository": repo_full_name,
                    "Issue URL": issue["html_url"],
                    "Issue Title": issue["title"],
                    "Issue Body": issue["body"],
                    "Created At": issue["created_at"],
                    "Updated At": issue["updated_at"],
                    "Labels": ", ".join(label["name"] for label in issue["labels"]),
                    "Comments": issue["comments"],
                    "Total Reactions": issue["reactions"]["total_count"],
                }
            )
            if len(all_issues) >= max_issues:
                break
        url = (
            get_next_page_link(response.headers.get("Link", ""))
            if len(all_issues) < max_issues
            else None
        )
    return all_issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_issues", type=int, default=30, help="Max issues per repo"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Look at issues from the last X days"
    )
    parser.add_argument("--output", type=str, required=True, help="Output CSV file")
    args = parser.parse_args()

    repos = get_starred_repos()
    all_issues = []

    for repo in repos:
        try:
            logging.info(f"Processing {repo}")
            all_issues.extend(get_issues(repo, args.max_issues, args.days))
        except Exception as e:
            logging.error(f"Failed to process repo {repo}: {str(e)}")
            continue

        # Write issues to CSV file after each repo
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Repository",
                    "Issue URL",
                    "Issue Title",
                    "Issue Body",
                    "Created At",
                    "Updated At",
                    "Labels",
                    "Comments",
                    "Total Reactions",
                ],
            )
            writer.writeheader()
            writer.writerows(all_issues)


if __name__ == "__main__":
    main()
