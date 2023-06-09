"""
Server to display GitHub issues from a provided CSV file.

Author: GPT-4

Usage:
  python serve_github_issues.py <input.csv> --port <port>
"""

import argparse
from datetime import datetime
import csv
import random
import sys
from marko import Markdown
from marko.ext.gfm import GFM
from flask import Flask, request, render_template_string, Markup
from werkzeug.exceptions import NotFound

markdown = Markdown(extensions=["codehilite"])
markdown.use(GFM)

# Increase CSV field size limit
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

# Read arguments
parser = argparse.ArgumentParser()
parser.add_argument("csvfile", type=str, help="Input CSV file")
parser.add_argument(
    "--port", type=int, default=5000, help="Port number to run the server on"
)
args = parser.parse_args()

# Load issues from CSV
issues = []
with open(args.csvfile, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Format the dates in a more human-readable way
        row["Created At"] = datetime.strptime(
            row["Created At"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%b %d, %Y %H:%M:%S")
        row["Updated At"] = datetime.strptime(
            row["Updated At"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%b %d, %Y %H:%M:%S")
        issues.append(row)

SORTED_ISSUES = {
    "created_at": sorted(
        issues,
        key=lambda x: datetime.strptime(x["Created At"], "%b %d, %Y %H:%M:%S"),
        reverse=True,
    ),
    "updated_at": sorted(
        issues,
        key=lambda x: datetime.strptime(x["Updated At"], "%b %d, %Y %H:%M:%S"),
        reverse=True,
    ),
    "total_reactions": sorted(
        issues, key=lambda x: int(x["Total Reactions"]), reverse=True
    ),
    "repo_name": sorted(issues, key=lambda x: x["Repository"]),
    "comments": sorted(issues, key=lambda x: int(x["Comments"]), reverse=True),
}

# Initialize Flask app
app = Flask(__name__)


@app.route("/")
def homepage():
    sort = request.args.get("sort", default="created_at", type=str)
    return render_template_string(
        """
    <!doctype html>
    <html>
    <head>
      <title>GitHub Issues</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 1em;
        }
    
        .sort-bar {
          background-color: #f2f2f2;
          padding: 0.5em;
          position: sticky;
          top: 0;
          z-index: 1;
        }
    
        .sort-bar a {
          margin-right: 1em;
          text-decoration: none;
          color: #007BFF;
        }
    
        .sort-bar a:not(:last-child)::after {
          content: '|';
          margin-left: 1em;
          color: #bbb;
        }
    
        .container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1em;
        }
    
        .card {
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 1em;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }
    
        .card h2 {
          margin-top: 0;
          margin-bottom: 0.5em;
          font-size: 1.2em;
        }
    
        .card p {
          margin: 0;
          margin-bottom: 0.2em;
          line-height: 1.2;
        }
    
        .card .tags {
          display: flex;
          flex-wrap: wrap;
          margin-top: 0.5em;
        }
    
        .card .tag {
          background-color: #eee;
          border-radius: 3px;
          padding: 0.3em 0.6em;
          margin-right: 0.6em;
          margin-bottom: 0.6em;
          font-size: 0.85em;
        }
    
        .empty-message {
          text-align: center;
          font-size: 1.2em;
          color: #888;
          margin: 2em;
        }
    
        a {
          color: #007BFF;
          text-decoration: none;
        }
    
        a:hover {
          text-decoration: underline;
        }
      </style>
    </head>
    <body>
      <div class="sort-bar">
        <span>Sort by:</span>
        <a href="/?sort=repo_name">Repository Name</a>
        <a href="/?sort=created_at">Created At</a>
        <a href="/?sort=updated_at">Updated At</a>
        <a href="/?sort=total_reactions">Total Reactions</a>
        <a href="/?sort=comments">Comments</a>
      </div>
      <div class="container">
        {% for issue in issues %}
          <div class="card">
            <h2>
              <a href="/{{ loop.index }}?sort={{ sort }}">
                {{ issue['Issue Title'] }}
              </a>
            </h2>
            <p>
              <a href="{{ issue['Issue URL'] }}" target="_blank" rel="noopener noreferrer">
                <strong>Comments:</strong> {{ issue['Comments'] }}
              </a>
            </p>
            <p><strong>Repository:</strong> {{ issue['Repository'] }}</p>
            <p><strong>Created at:</strong> {{ issue['Created At'] }}</p>
            <p><strong>Updated at:</strong> {{ issue['Updated At'] }}</p>
            <p><strong>Total reactions:</strong> {{ issue['Total Reactions'] }}</p>
            {% if issue['Labels'] %}
              <div class="tags">
                {% for label in issue['Labels'].split(', ') %}
                  <span class="tag">{{ label }}</span>
                {% endfor %}
              </div>
            {% endif %}
          </div>
        {% endfor %}
        {% if not issues %}
          <p class="empty-message">No issues found.</p>
        {% endif %}
      </div>
    </body>
    </html>
    """,
        issues=SORTED_ISSUES[sort],
        sort=sort,
    )


@app.route("/<int:issue_num>")
def get_issue(issue_num):
    sort = request.args.get("sort", default="created_at", type=str)
    try:
        issue = SORTED_ISSUES[sort][
            issue_num - 1
        ]  # Subtract 1 because indexing starts from 0
    except IndexError:
        raise NotFound("Issue not found")

    # Convert Markdown to HTML
    issue_body_html = Markup(markdown(issue["Issue Body"]))

    # Render issue details
    return render_template_string(
        """
    <!doctype html>
    <html>
    <head>
      <title>Issue {{ issue_num }}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 1em;
        }

        .navbar {
          background-color: #f2f2f2;
          padding: 0.5em;
          position: sticky;
          top: 0;
          z-index: 1;
          max-width: 800px;
          margin: 0 auto;
        }

        .navbar a {
          margin-right: 1em;
          text-decoration: none;
          color: #007BFF;
        }

        .navbar a:not(:last-child)::after {
          content: '|';
          margin-left: 1em;
          color: #bbb;
        }

        .container {
          max-width: 800px;
          margin: 0 auto;
        }

        h1 {
          color: #333;
          font-size: 1.8em;
          margin-top: 0;
          margin-bottom: 0.5em;
        }

        p {
          margin: 0;
          margin-bottom: 0.2em;
          line-height: 1.4;
        }

        .metadata {
          margin-top: 1em;
        }

        .metadata p {
          font-size: 0.9em;
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

        .issue-body {
          margin-top: 1em;
        }

        a {
          color: #007BFF;
          text-decoration: none;
        }

        a:hover {
          text-decoration: underline;
        }

        pre { line-height: 125%; padding: 16px; }
        td.linenos .normal { color: inherit; background-color: transparent; padding-left: 5px; padding-right: 5px; }
        span.linenos { color: inherit; background-color: transparent; padding-left: 5px; padding-right: 5px; }
        td.linenos .special { color: #000000; background-color: #ffffc0; padding-left: 5px; padding-right: 5px; }
        span.linenos.special { color: #000000; background-color: #ffffc0; padding-left: 5px; padding-right: 5px; }
        .highlight .hll { background-color: #ffffcc }
        .highlight { background: #f8f8f8; }
        .highlight .c { color: #3D7B7B; font-style: italic } /* Comment */
        .highlight .err { border: 1px solid #FF0000 } /* Error */
        .highlight .k { color: #008000; font-weight: bold } /* Keyword */
        .highlight .o { color: #666666 } /* Operator */
        .highlight .ch { color: #3D7B7B; font-style: italic } /* Comment.Hashbang */
        .highlight .cm { color: #3D7B7B; font-style: italic } /* Comment.Multiline */
        .highlight .cp { color: #9C6500 } /* Comment.Preproc */
        .highlight .cpf { color: #3D7B7B; font-style: italic } /* Comment.PreprocFile */
        .highlight .c1 { color: #3D7B7B; font-style: italic } /* Comment.Single */
        .highlight .cs { color: #3D7B7B; font-style: italic } /* Comment.Special */
        .highlight .gd { color: #A00000 } /* Generic.Deleted */
        .highlight .ge { font-style: italic } /* Generic.Emph */
        .highlight .gr { color: #E40000 } /* Generic.Error */
        .highlight .gh { color: #000080; font-weight: bold } /* Generic.Heading */
        .highlight .gi { color: #008400 } /* Generic.Inserted */
        .highlight .go { color: #717171 } /* Generic.Output */
        .highlight .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
        .highlight .gs { font-weight: bold } /* Generic.Strong */
        .highlight .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
        .highlight .gt { color: #0044DD } /* Generic.Traceback */
        .highlight .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
        .highlight .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
        .highlight .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
        .highlight .kp { color: #008000 } /* Keyword.Pseudo */
        .highlight .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
        .highlight .kt { color: #B00040 } /* Keyword.Type */
        .highlight .m { color: #666666 } /* Literal.Number */
        .highlight .s { color: #BA2121 } /* Literal.String */
        .highlight .na { color: #687822 } /* Name.Attribute */
        .highlight .nb { color: #008000 } /* Name.Builtin */
        .highlight .nc { color: #0000FF; font-weight: bold } /* Name.Class */
        .highlight .no { color: #880000 } /* Name.Constant */
        .highlight .nd { color: #AA22FF } /* Name.Decorator */
        .highlight .ni { color: #717171; font-weight: bold } /* Name.Entity */
        .highlight .ne { color: #CB3F38; font-weight: bold } /* Name.Exception */
        .highlight .nf { color: #0000FF } /* Name.Function */
        .highlight .nl { color: #767600 } /* Name.Label */
        .highlight .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
        .highlight .nt { color: #008000; font-weight: bold } /* Name.Tag */
        .highlight .nv { color: #19177C } /* Name.Variable */
        .highlight .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
        .highlight .w { color: #bbbbbb } /* Text.Whitespace */
        .highlight .mb { color: #666666 } /* Literal.Number.Bin */
        .highlight .mf { color: #666666 } /* Literal.Number.Float */
        .highlight .mh { color: #666666 } /* Literal.Number.Hex */
        .highlight .mi { color: #666666 } /* Literal.Number.Integer */
        .highlight .mo { color: #666666 } /* Literal.Number.Oct */
        .highlight .sa { color: #BA2121 } /* Literal.String.Affix */
        .highlight .sb { color: #BA2121 } /* Literal.String.Backtick */
        .highlight .sc { color: #BA2121 } /* Literal.String.Char */
        .highlight .dl { color: #BA2121 } /* Literal.String.Delimiter */
        .highlight .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
        .highlight .s2 { color: #BA2121 } /* Literal.String.Double */
        .highlight .se { color: #AA5D1F; font-weight: bold } /* Literal.String.Escape */
        .highlight .sh { color: #BA2121 } /* Literal.String.Heredoc */
        .highlight .si { color: #A45A77; font-weight: bold } /* Literal.String.Interpol */
        .highlight .sx { color: #008000 } /* Literal.String.Other */
        .highlight .sr { color: #A45A77 } /* Literal.String.Regex */
        .highlight .s1 { color: #BA2121 } /* Literal.String.Single */
        .highlight .ss { color: #19177C } /* Literal.String.Symbol */
        .highlight .bp { color: #008000 } /* Name.Builtin.Pseudo */
        .highlight .fm { color: #0000FF } /* Name.Function.Magic */
        .highlight .vc { color: #19177C } /* Name.Variable.Class */
        .highlight .vg { color: #19177C } /* Name.Variable.Global */
        .highlight .vi { color: #19177C } /* Name.Variable.Instance */
        .highlight .vm { color: #19177C } /* Name.Variable.Magic */
        .highlight .il { color: #666666 } /* Literal.Number.Integer.Long */

      </style>
    </head>
    <body>
      <div class="navbar">
        <a href="/">Home</a>
        <a href="/1?sort={{ sort }}">First</a>
        <a href="/{{ prev_issue_num }}?sort={{ sort }}">Previous</a>
        <a href="/{{ random_issue_num }}?sort={{ sort }}">Random</a>
        <a href="/{{ next_issue_num }}?sort={{ sort }}">Next</a>
        <a href="/{{ num_issues }}?sort={{ sort }}">Last</a>
      </div>
      <div class="container">
        <h1><a href="{{ issue['Issue URL'] }}" target="_blank" rel="noopener noreferrer">{{ issue['Issue Title'] }}</a></h1>
        <div class="metadata">
          <p>
            <a href="{{ issue['Issue URL'] }}" target="_blank" rel="noopener noreferrer">
              <strong>Comments:</strong> {{ issue['Comments'] }}
            </a>
          </p>
          <p><strong>Repository:</strong> {{ issue['Repository'] }}</p>
          <p><strong>Created at:</strong> {{ issue['Created At'] }}</p>
          <p><strong>Updated at:</strong> {{ issue['Updated At'] }}</p>
          <p><strong>Total reactions:</strong> {{ issue['Total Reactions'] }}</p>
        </div>
        {% if issue['Labels'] %}
          <div class="labels">
            {% for label in issue['Labels'].split(', ') %}
              <span class="label">{{ label }}</span>
            {% endfor %}
          </div>
        {% endif %}
        <div class="issue-body">{{ issue_body_html }}</div>
      </div>
    </body>
    </html>
    """,
        issue=issue,
        issue_num=issue_num,
        issue_body_html=issue_body_html,
        num_issues=len(SORTED_ISSUES[sort]),
        sort=sort,
        prev_issue_num=max(1, issue_num - 1),
        random_issue_num=random.randint(1, len(SORTED_ISSUES[sort])),
        next_issue_num=min(issue_num + 1, len(SORTED_ISSUES[sort])),
    )


if __name__ == "__main__":
    app.run(port=args.port)
