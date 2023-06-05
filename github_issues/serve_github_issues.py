"""
Server to display GitHub issues from a provided CSV file.

Author: GPT-4

Usage:
  python serve_github_issues.py <input.csv> --port <port>
"""

import argparse
from datetime import datetime
import csv
import markdown
import random
import sys
from flask import Flask, request, render_template_string, Markup
from werkzeug.exceptions import NotFound

# Increase CSV field size limit
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

# Read arguments
parser = argparse.ArgumentParser()
parser.add_argument('csvfile', type=str, help='Input CSV file')
parser.add_argument('--port', type=int, default=5000, help='Port number to run the server on')
args = parser.parse_args()

# Load issues from CSV
with open(args.csvfile, 'r') as f:
    reader = csv.DictReader(f)
    issues = list(reader)

SORTED_ISSUES = {
    'created_at': sorted(issues, key=lambda x: datetime.strptime(x['Created At'], '%Y-%m-%dT%H:%M:%SZ'), reverse=True),
    'updated_at': sorted(issues, key=lambda x: datetime.strptime(x['Updated At'], '%Y-%m-%dT%H:%M:%SZ'), reverse=True),
    'total_reactions': sorted(issues, key=lambda x: int(x['Total Reactions']), reverse=True),
    'repo_name': sorted(issues, key=lambda x: x['Repository']),
}

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def homepage():
    sort = request.args.get('sort', default='created_at', type=str)
    return render_template_string("""
    <!doctype html>
    <html>
    <head>
      <title>GitHub Issues</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0 auto;
          max-width: 800px;
          padding: 1em;
        }

        table {
          border-collapse: collapse;
          width: 100%;
        }

        th, td {
          border: 1px solid #ddd;
          padding: 8px;
        }

        th {
          background-color: #f2f2f2;
          font-weight: bold;
          text-align: left;
        }

        tr:nth-child(even) {
          background-color: #f9f9f9;
        }

        tr:hover {
          background-color: #f5f5f5;
        }

        .navigation {
          margin-bottom: 2em;
        }

        .navigation a {
          margin-right: 1em;
          text-decoration: none;
          color: #007BFF;
        }

        .navigation a:hover {
          color: #0056b3;
        }
      </style>
    </head>
    <body>
      <div class="navigation">
        <a href="/?sort=repo_name">Sort by Repository Name</a>
        <a href="/?sort=created_at">Sort by Created At</a>
        <a href="/?sort=updated_at">Sort by Updated At</a>
        <a href="/?sort=total_reactions">Sort by Total Reactions</a>
      </div>
      <table>
        <thead>
          <tr>
            <th>Repository</th>
            <th>Issue Title</th>
            <th>Created At</th>
            <th>Total Reactions</th>
          </tr>
        </thead>
        <tbody>
          {% for issue in issues %}
            <tr>
              <td>{{ issue['Repository'] }}</td>
              <td><a href="/{{ loop.index }}?sort={{ sort }}">{{ issue['Issue Title'] }}</a></td>
              <td>{{ issue['Created At'] }}</td>
              <td>{{ issue['Total Reactions'] }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </body>
    </html>
    """, issues=SORTED_ISSUES[sort], sort=sort)

@app.route('/<int:issue_num>')
def get_issue(issue_num):
    sort = request.args.get('sort', default='created_at', type=str)
    try:
        issue = SORTED_ISSUES[sort][issue_num - 1]  # Subtract 1 because indexing starts from 0
    except IndexError:
        raise NotFound("Issue not found")

    # Convert GitHub-flavored markdown to HTML
    issue_body_html = Markup(markdown.markdown(issue['Issue Body'], extensions=['fenced_code', 'tables']))

    # Render issue details
    return render_template_string("""
    <!doctype html>
    <html>
    <head>
      <title>Issue {{ issue_num }}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0 auto;
          max-width: 800px;
          padding: 1em;
        }

        h1 {
          color: #333;
        }

        p {
          line-height: 1.6;
        }

        .labels {
          margin-top: 1em;
        }

        .label {
          display: inline-block;
          background-color: #eee;
          border-radius: 3px;
          padding: 0.3em 0.6em;
          margin-right: 0.6em;
          margin-bottom: 0.6em;
          font-size: 0.85em;
        }

        .navigation {
          margin-bottom: 2em;
        }

        .navigation a {
          margin-right: 1em;
          text-decoration: none;
          color: #007BFF;
        }

        .navigation a:hover {
          color: #0056b3;
        }
      </style>
    </head>
    <body>
      <div class="navigation">
        <a href="/">Home</a>
        <a href="/1?sort={{ sort }}">First</a>
        <a href="/{{ prev_issue_num }}?sort={{ sort }}">Previous</a>
        <a href="/{{ random_issue_num }}?sort={{ sort }}">Random</a>
        <a href="/{{ next_issue_num }}?sort={{ sort }}">Next</a>
        <a href="/{{ num_issues }}?sort={{ sort }}">Last</a>
      </div>
      <h1><a href="{{ issue['Issue URL'] }}">{{ issue['Issue Title'] }}</a></h1>
      <p><strong>Repository:</strong> {{ issue['Repository'] }}</p>
      <p><strong>Created at:</strong> {{ issue['Created At'] }}</p>
      <p><strong>Total reactions:</strong> {{ issue['Total Reactions'] }}</p>
      <div class="labels">
        {% for label in issue['Labels'].split(', ') %}
          <span class="label">{{ label }}</span>
        {% endfor %}
      </div>
      <div>{{ issue_body_html }}</div>
    </body>
    </html>
    """, issue=issue, issue_num=issue_num, issue_body_html=issue_body_html,
    num_issues=len(SORTED_ISSUES[sort]), sort=sort,
    prev_issue_num=max(1, issue_num-1), random_issue_num=random.randint(1, len(SORTED_ISSUES[sort])),
    next_issue_num=min(issue_num+1, len(SORTED_ISSUES[sort])))

if __name__ == '__main__':
    app.run(port=args.port)
