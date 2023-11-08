"""
Makes repositories starred on `API_TOKEN` get watched on `BURNER_API_TOKEN`.

Author: GPT-4

Usage:
  python watch_on_burner.py
"""

__author__ = "GPT-4"

import os
import requests
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
BURNER_API_TOKEN = os.getenv("BURNER_API_TOKEN")

headers = {"Authorization": f"token {API_TOKEN}"}
burner_headers = {"Authorization": f"token {BURNER_API_TOKEN}"}

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

def watch_repo_on_burner(repo_name: str) -> None:
    url = f"https://api.github.com/repos/{repo_name}/subscription"
    data = {
        "subscribed": True
    }
    response = requests.put(url, headers=burner_headers, json=data)
    response.raise_for_status()

if __name__ == "__main__":
    starred_repos = get_starred_repos()
    for repo in starred_repos:
        print(f"Watching {repo} on burner account...")
        watch_repo_on_burner(repo)
    print("Done!")
