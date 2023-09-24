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
2. Change to the `contributor-tools` directory.
3. Create and activate a virtual environment, e.g.:
 - `python -m venv ../venvs/contributor-tools`
 - `source ../venvs/contributor-tools/bin/activate` (Posix) `.\venvs\contributor-tools\Scripts\activate` (Windows)
4. Install the required Python packages by running: `pip install -r requirements.txt`
5. Change to the `github_issues` directory.
6. Create  a [fine-grained GitHub Personal Access Token](https://github.com/settings/tokens?type=beta) (PAT)
 - Generate new token
 - Confirm access 
 - Check All repositories (or up to 50 selected repositories)
 - Permissions -> Repository permissions -> Issues -> Access: Read-only
 - Permissions -> Account permissions -> Starring -> Access: Read-only
 - Generate token.
 - Copy its value.
7. Create a `.env` file in the root of the project directory (`contributor-tools/github_issues`) containing this PAT:
 - `echo API_TOKEN=your-github-PAT > .env` where your-github-PAT is the token created in the previous step.

## Scripts

The `contributor-tools/github_issues` directory contains the following scripts:

1. `pull_github_issues.py`: This script pulls open GitHub issues from repositories you have starred and saves them in a CSV file. You can specify the maximum number of issues per repository and the number of days to consider. Usage: `python pull_github_issues.py --max_issues <max_issues> --days <days> --output <output.csv>`

2. `get_help_wanted.py`: This script filters the GitHub issues CSV file and includes only the issues that are open to contributors. You can filter by good first issues or issues accepting pull requests. Usage: `python get_help_wanted.py <input.csv> --output <output.csv> [--good-first-issue] [--accepting-prs]`

3. `merge_issue_csvs.py`: This script merges multiple GitHub issues CSV files and deduplicates them based on the 'Issue URL'. The script is useful when you have issue data from multiple CSV files that you want to combine into a single file. Usage: `python merge.py a.csv b.csv c.csv -o d.csv`.

4. `serve_github_issues.py`: This script serves the filtered GitHub issues as a web application. You can view the issues in a browser, navigate between them, and sort them based on different criteria. Usage: `python serve_github_issues.py <input.csv> --port <port>`


Please refer to the individual script docstrings for more detailed usage instructions.

## Roadmap
We will see if GPT-4 can (ML-generated ML!):
* Use textual analysis to classify issues (first issues / accepting pr / blocked) without explicit tags
* Add a Tinder swipe -like feedback mechanism which improves recommendations over time
