# Local storage format: `dataExports/`

This document defines how data downloaded from Gmail, GitHub, Notion and Linear is stored locally. Every exporter (human or Claude) must follow it exactly.

## Folder structure

```
dataExports/
├── gmail/    # one file per email message
├── github/   # one file per repository
├── notion/   # one file per page
└── linear/   # one file per issue
```

One sub-folder per service, named in lowercase. Nothing else goes inside the service folders except `.gitkeep`.

## File naming

```
<YYYY-MM-DD_HH-MM-SS>_<short-id>.json
```

- **Timestamp** is the item's `created` value (received time for emails), converted to **UTC**, formatted `%Y-%m-%d_%H-%M-%S`. Fractional seconds are dropped.
- **Short-id** depends on the service:

| Service | Short-id rule | Example filename |
|---|---|---|
| gmail | **last** 8 characters of the Gmail message id (the first characters are nearly identical across messages, so they are not unique) | `2026-10-15_23-44-19_ecf43b32.json` |
| github | repository name (without owner) | `2026-10-15_22-47-59_atlas-api-gateway.json` |
| notion | page id without dashes: first 8 + last 4 hex characters | `2026-10-15_22-49-00_3fa6f755ec5f.json` |
| linear | issue identifier | `2026-10-15_22-49-40_ABR-12.json` |

Files are UTF-8 JSON, pretty-printed with 2-space indent, non-ASCII characters kept as-is (not `\u` escaped), ending with a newline.

## Shared fields

Every file is one JSON object with these top-level fields, in this order:

| Field | Type | Meaning |
|---|---|---|
| `service` | string | `gmail`, `github`, `notion` or `linear` |
| `id` | string | The service's own full id (Gmail message id, GitHub numeric repo id as a string, Notion page UUID with dashes, Linear identifier) |
| `title` | string | Email subject, `owner/repo`, page title (without emoji icon), or issue title |
| `body` | string | Full text: email plain-text body, README text, page content as Notion Markdown, or issue description. Never truncated. |
| `author` | string | Sender address, repo owner login, page creator name, or issue creator name |
| `created` | string | ISO 8601 UTC timestamp, as returned by the service |
| `updated` | string | ISO 8601 UTC timestamp of last change |
| `url` | string | Link to the item in the service's web UI |
| `metadata` | object | Service-specific details, see below |

## Service-specific metadata

### gmail
| Key | Type | Notes |
|---|---|---|
| `from` | string | Sender address |
| `to` | string[] | Recipient addresses |
| `cc` | string[] | CC addresses (empty array if none) |
| `date` | string | Message date, ISO 8601 UTC |
| `labels` | string[] | Gmail label ids, e.g. `INBOX`, `SENT`, `UNREAD`, `CATEGORY_UPDATES` |
| `threadId` | string | Gmail thread id |

### github
| Key | Type | Notes |
|---|---|---|
| `description` | string \| null | Repo description |
| `language` | string \| null | Primary language as detected by GitHub |
| `visibility` | string | `public` or `private` |
| `default_branch` | string | e.g. `main` |
| `readme` | string \| null | Full README text (same text as `body`) |

### notion
| Key | Type | Notes |
|---|---|---|
| `parent` | object | `{ "type": "workspace" \| "page" \| "database", "name": ..., "id"?: ... }` |
| `properties` | object | Page properties as returned by the Notion fetch tool (at least `title`) |
| `icon` | string \| null | Emoji icon, if any |

### linear
| Key | Type | Notes |
|---|---|---|
| `identifier` | string | e.g. `ABR-12` |
| `status` | string | Workflow state name, e.g. `Backlog` |
| `priority` | string | `No priority`, `Urgent`, `High`, `Medium` or `Low` |
| `assignee` | string \| null | Assignee name |
| `labels` | string[] | Label names (empty array if none) |
| `team` | string | Team name |
| `project` | string \| null | Project name |

## Nullable and approximate fields

| Field | Service | Why |
|---|---|---|
| `updated` = `created` | gmail | Emails are immutable; each export is a single message. |
| `cc` = `[]` | gmail | Message had no CC recipients. |
| `metadata.language` = `null` | github | GitHub reports no language for repos that only contain Markdown/config files. |
| `metadata.description` = `null` | github | Repo has no description set. |
| `created` (approximate) | notion | The Notion fetch tool does not return a page's created time. The `timestamp` from `notion-search` results is used instead (minute precision, e.g. `22:49:00.000Z`), so several pages can share the same filename timestamp. |
| `updated` | notion | Taken from `page_last_edited_at` returned by `notion-fetch`. |
| `author` (approximate) | notion | Not returned by the fetch tool; set to the connected user's name from `notion-get-self`. |
| `parent` (approximate) | notion | Top-level pages have an empty ancestor path; recorded as the workspace from `notion-get-self`. |
| `updated` = `created` | linear | Used when `list_issues` returns no newer `updatedAt`. |
| `metadata.assignee` = `null` | linear | Issue is unassigned. |
| `metadata.project` = `null` | linear | Issue belongs to no project. |
| `author` = `null` | linear | Linear's built-in onboarding issues (ABR-1 to ABR-4) have no `createdBy`. |
| `url` = message `viewUrl` | gmail | For threads with several messages, each file uses its own message link (ending in `msg-f:<id>`) so that files in the same thread don't share a URL. |
| `metadata.readme` = `null`, `body` = `""` | github | Repo has no `README.md`. |
| `body` = `""` | notion | Page is blank (the fetch tool returns `<blank-page>`). |
| `metadata.icon` = `null` | notion | Page has no icon, or has a built-in Notion icon (e.g. `icons/checklist_green`) instead of an emoji. |
| `parent` = database / page | notion | Rows of the "Todo List" database record `{ "type": "database", "name", "id" }`; nested sub-pages record their direct parent page. |

## Examples

Long `body` and `readme` values are shortened with `…` here only; real files contain the full text.

### gmail — `dataExports/gmail/2026-10-15_23-44-19_ecf43b32.json`
```json
{
  "service": "gmail",
  "id": "1a141f3cecf43b32",
  "title": "Project Atlas kickoff recap",
  "body": "Hi team,\n\nThanks for joining the Project Atlas kickoff today. Quick recap:\n\n- Goal: launch the new route-optimization engine for Lumen Freight by end of Q1.\n- Joe Smith will own the backend architecture …",
  "author": "abrahamaiproject@gmail.com",
  "created": "2026-10-15T23:44:19Z",
  "updated": "2026-10-15T23:44:19Z",
  "url": "https://mail.google.com/mail/?authuser=abrahamaiproject@gmail.com#all/thread-f:1879161291054267186",
  "metadata": {
    "from": "abrahamaiproject@gmail.com",
    "to": ["abrahamaiproject@gmail.com"],
    "cc": [],
    "date": "2026-10-15T23:44:19Z",
    "labels": ["UNREAD", "SENT", "INBOX"],
    "threadId": "1a141f3cecf43b32"
  }
}
```

### github — `dataExports/github/2026-10-15_22-47-59_atlas-api-gateway.json`
```json
{
  "service": "github",
  "id": "1421401129",
  "title": "abrahamaiproject-bit/atlas-api-gateway",
  "body": "# atlas-api-gateway\n\nPublic REST gateway for **Project Atlas**. …",
  "author": "abrahamaiproject-bit",
  "created": "2026-10-15T22:47:59Z",
  "updated": "2026-10-15T22:48:56Z",
  "url": "https://github.com/abrahamaiproject-bit/atlas-api-gateway",
  "metadata": {
    "description": "Public REST gateway for Project Atlas",
    "language": null,
    "visibility": "private",
    "default_branch": "main",
    "readme": "# atlas-api-gateway\n\nPublic REST gateway for **Project Atlas**. …"
  }
}
```

### notion — `dataExports/notion/2026-10-15_22-49-00_3fa6f755ec5f.json`
```json
{
  "service": "notion",
  "id": "3fa6f755-57f6-810e-86b7-c3e3a91eec5f",
  "title": "Harbor Logistics Pilot Plan",
  "body": "## Scope\n45 trucks at the Newark and Philadelphia depots, running for 90 days starting November 3.\n## Success criteria\n- 8% reduction in miles driven\n- 95% on-time delivery\nThe pilot runs on Project Atlas. Joe Smith is the technical point of contact.",
  "author": "Abraham AIProject",
  "created": "2026-10-15T22:49:00.000Z",
  "updated": "2026-10-15T22:49:16.477Z",
  "url": "https://app.notion.com/p/3fa6f75557f6810e86b7c3e3a91eec5f",
  "metadata": {
    "parent": { "type": "workspace", "name": "Abraham AIProject’s Space" },
    "properties": { "title": "Harbor Logistics Pilot Plan" },
    "icon": "🚚"
  }
}
```

### linear — `dataExports/linear/2026-10-15_22-49-40_ABR-12.json`
```json
{
  "service": "linear",
  "id": "ABR-12",
  "title": "[Project Atlas] Live traffic re-optimization",
  "body": "Use speed features from telemetry-pipeline to re-plan routes mid-day when delays exceed 15 minutes. Design review with Joe Smith needed before implementation.",
  "author": "Abraham AIProject",
  "created": "2026-10-15T22:49:40.963Z",
  "updated": "2026-10-15T22:49:40.963Z",
  "url": "https://linear.app/abraham-gabay/issue/ABR-12/project-atlas-live-traffic-re-optimization",
  "metadata": {
    "identifier": "ABR-12",
    "status": "Backlog",
    "priority": "Medium",
    "assignee": null,
    "labels": [],
    "team": "Abraham Gabay",
    "project": null
  }
}
```
