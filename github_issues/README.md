Almost everything here, including this README, was written by GPT-3.5 and GPT-4.

# GitHub Issues Contributor Tools

This repository contains a set of tools to help you explore and filter open GitHub issues from repositories you have starred. The tools consist of three Python scripts: `pull_github_issues.py`, `get_help_wanted.py`, and `serve_github_issues.py`. These scripts allow you to pull open GitHub issues, filter them based on tags, and serve them as a web application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Scripts](#scripts)
- [Roadmap](#roadmap)

## Prerequisites

To use these tools, you need to have the following software installed:

- Python 3.x
- pip package manager

## Usage

To get started, follow these steps:

1. Clone this repository to your local machine.
2. Change to the `contributor-tools/github_issues` directory.
3. Create a `.env` file in the root of the project directory (`contributor-tools/github_issues`) and add the following line to it:
```
API_TOKEN=your-github-api-token
```
Replace `your-github-api-token` with your actual GitHub API token (Settings > Developer settings > Personal access tokens).

4. Install the required Python packages by running: `pip install -r requirements.txt`

## Scripts

The `contributor-tools/github_issues` directory contains the following scripts:

1. `pull_github_issues.py`: This script pulls open GitHub issues from repositories you have starred and saves them in a CSV file. You can specify the maximum number of issues per repository and the number of days to consider. Usage: `python pull_github_issues.py --max_issues <max_issues> --days <days> --output <output.csv>`

2. `get_help_wanted.py`: This script filters the GitHub issues CSV file and includes only the issues that are open to contributors. You can filter by good first issues or issues accepting pull requests. Usage: `python get_help_wanted.py <input.csv> --output <output.csv> [--good-first-issue] [--accepting-prs]`

3. `serve_github_issues.py`: This script serves the filtered GitHub issues as a web application. You can view the issues in a browser, navigate between them, and sort them based on different criteria. Usage: `python serve_github_issues.py <input.csv> --port <port>`

Please refer to the individual script docstrings for more detailed usage instructions.

## Roadmap
We will see if GPT-4 can (ML-generated ML!):
* Use textual analysis to classify issues (first issues / accepting pr / blocked) without explicit tags
* Add a Tinder swipe -like feedback mechanism which improves recommendations over time
