# AI Homework 3 — Claude Code + MCP data exports

A class assignment that connects **Claude Code** to six services — **Gmail, GitHub,
Notion, Linear, Todoist and Jira** — through MCP (Model Context Protocol) servers, downloads their
data into local JSON files, and lets you search everything in a small local dashboard.

## Team and contributions

| Member | Contributions |
|---|---|
| _Name_ | _To be filled in_ |
| _Name_ | _To be filled in_ |

## How each service is connected

| Service | How | Auth | Items exported |
|---|---|---|---|
| GitHub | `.mcp.json` → GitHub's remote MCP server (`https://api.githubcopilot.com/mcp/`) | Personal access token read from the `GITHUB_PAT` environment variable | 11 repositories |
| Notion | `.mcp.json` → Notion's remote MCP server (`https://mcp.notion.com/mcp`) | OAuth sign-in when first used | 20 pages |
| Linear | `.mcp.json` → Linear's remote MCP server (`https://mcp.linear.app/mcp`) | OAuth sign-in when first used | 14 issues |
| Todoist | `.mcp.json` → Todoist's official remote MCP server (`https://ai.todoist.net/mcp`) | OAuth sign-in in the browser when first used | 10 tasks |
| Jira | `.mcp.json` → Atlassian's official remote MCP server (`https://mcp.atlassian.com/v1/mcp/authv2`) | OAuth sign-in in the browser when first used | 23 issues |
| Gmail | Google's official Gmail MCP server, through the **claude.ai Gmail connector** | Google sign-in on claude.ai | 24 emails |

**Why Gmail is different:** using Google's Gmail MCP server with your own OAuth client
requires joining Google's preview program, and that program doesn't accept personal
Gmail accounts. So Gmail goes through the claude.ai connector, which uses the same
official server, and it isn't listed in `.mcp.json`.

## Repository layout

```
.
├── .mcp.json                 # MCP server config for GitHub, Notion, Linear, Todoist and Jira
├── .claude/skills/
│   └── export-service-data/  # Claude Code skill that downloads data into dataExports/
├── localStorageFormats.md    # Spec for how exported data is stored (naming, fields, metadata)
├── dataExports/              # The downloaded data: one JSON file per item
│   ├── gmail/                #   emails
│   ├── github/               #   repositories
│   ├── notion/               #   pages
│   ├── linear/               #   issues
│   ├── todoist/              #   tasks
│   └── jira/                 #   issues
└── dashboard/                # Local search website (Python server + one HTML page)
```

To refresh the data, ask Claude Code to "export service data". The skill downloads only
items that aren't already in `dataExports/`.

## Running the dashboard

You need Python 3.8+ (no packages to install). From the repo root:

```bash
python3 dashboard/server.py
```

Then open **http://127.0.0.1:8765/**. The dashboard only reads the local JSON files and
never contacts the live services. You can search title, body and metadata across all
services at once, filter by service, and click any result to see the full item. See
[`dashboard/README.md`](dashboard/README.md) for details.

## Presentation and demo

| File | What it is |
|---|---|
| [`Homework3_Presentation.pptx`](Homework3_Presentation.pptx) | Slide deck presenting the project |
| [`videos/demo_video.mp4`](videos/demo_video.mp4) | Demo video: logging into Linear, downloading data with Claude Code, searching the dashboard |
| [`screenshots/`](screenshots/) | Original content and the same content in the dashboard for each service, plus the MCP connections and a cross-service search |

## Data and privacy

All data in this repo is **fictional test data** from throwaway accounts created for this
assignment. The repo contains **no secrets**: the GitHub token comes from an environment
variable, Notion, Linear, Todoist and Jira use OAuth, and `.gitignore` keeps out `.env` and credential files.
