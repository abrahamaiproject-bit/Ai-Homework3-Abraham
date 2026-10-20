---
name: export-service-data
description: Download items from Gmail (claude.ai Gmail connector), GitHub, Notion, Linear, Todoist and Jira into dataExports/<service>/ as one JSON file per item, following localStorageFormats.md, skipping items already downloaded. Use when asked to export, download, sync or refresh data from any of these services.
---

# Export service data

Download items from Gmail, GitHub, Notion, Linear, Todoist and Jira and store them in `dataExports/` **exactly** as specified in `localStorageFormats.md` at the project root. Read that file first; it is the source of truth for folder layout, file naming, short-id rules, field order, metadata keys and which fields may be null or approximate. If this skill and that file ever disagree, follow `localStorageFormats.md`.

## Inputs

- Which services (default: all six) and how many items per service (default: at least 5).
- Optional filters the user gives (e.g. a Gmail search query, a repo owner, a Notion keyword, a Linear team, a Todoist project, a Jira project key).

## Step 1 — Find what is already downloaded

Before calling any service, build the set of ids already on disk for each service:

```bash
for s in gmail github notion linear todoist jira; do
  echo "== $s"; for f in dataExports/$s/*.json; do [ -e "$f" ] && python3 -I -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$f"; done
done
```

Compare on the full `id` field (not the filename). Any item whose `id` is already present is **skipped**: do not fetch its full content and do not rewrite its file. Only re-download an existing item when the user explicitly asks to refresh it; then delete the old file first (its timestamp/short-id may differ) and write the new one.

When counting toward "at least N items", count only items you newly wrote plus those already on disk, and keep paging through results until the target is met or the service has no more items. Report how many were new vs. skipped.

## Step 2 — Fetch from each service

Load the deferred MCP tools with ToolSearch (`select:` the names below) before calling them.

### Gmail — claude.ai Gmail connector only
Use the `mcp__claude_ai_Gmail__*` tools, never another Gmail integration.
1. `search_threads` with the user's query (or `in:inbox`), `pageSize` as needed. Use `pageToken` to page.
2. For each message id not already on disk: `get_thread` with `messageFormat: "PLAIN_TEXT"`. Export **one file per message** (a multi-message thread produces several files, all with the same `metadata.threadId`).
3. Map: `id` = message id, `title` = subject, `body` = `plaintextBody` (full, unmodified), `author` = sender, `created` = `updated` = message `date`, `url` = the message/thread `viewUrl`, metadata `from`/`to`/`cc`/`date`/`labels` (= `labelIds`)/`threadId`. Use `[]` for missing `cc`.

### GitHub
1. `mcp__github__get_me` to get the login, then `mcp__github__search_repositories` with `query: "user:<login>"` and `minimal_output: false` (this includes private repos).
2. For each repo not on disk: `mcp__github__get_file_contents` with `path: "README.md"`. If it 404s, use `null` for `readme` and `""` for `body`.
3. Map: `id` = numeric repo id as string, `title` = `full_name`, `body` = README text, `author` = owner login, `created` = `created_at`, `updated` = `updated_at`, `url` = `html_url`, metadata `description`, `language` (null if absent), `visibility`, `default_branch`, `readme`.

### Notion
1. `notion-get-self` once, for `author` and the workspace `parent`.
2. `notion-search` with several short keywords to collect page ids (search results are keyword-based; one query rarely returns everything). Keep each result's `timestamp` — it is used as `created`.
3. For each page not on disk: `notion-fetch` with the page id. `body` = the text inside `<content>…</content>`, with Markdown escapes such as `\$` unescaped. `title` = the `title` property (no emoji). `updated` = `page_last_edited_at`. `url` = `https://app.notion.com/p/<id-without-dashes>`. metadata `parent` (from `<ancestor-path>`, or the workspace if empty), `properties` (the `<properties>` JSON), `icon`.
4. Skip database/data-source results; export pages only.

### Linear
1. `mcp__linear__list_issues` with `fields: ["id","title","description","url","createdAt","updatedAt","status","priority","assignee","labels","createdBy","team","project"]`, paging with `cursor`.
2. Map: `id` = identifier (e.g. `ABR-12`), `title`, `body` = `description` (full; use `mcp__linear__get_issue` if a description looks truncated), `author` = `createdBy`, `created` = `createdAt`, `updated` = `updatedAt` (or `createdAt` if absent), `url`, metadata `identifier`, `status`, `priority` (= `priority.name`), `assignee`, `labels` (names), `team`, `project`.

### Todoist
1. `mcp__todoist__user-info` once, for `author` (the connected user's `fullName`).
2. `mcp__todoist__find-projects` to list projects (id → name); `mcp__todoist__find-sections` per project for section names.
3. `mcp__todoist__find-tasks` per project (`projectId`, including `"inbox"`) with `responsibleUserFiltering: "all"` and `limit: 100`, paging with `cursor`. Include completed tasks with `mcp__todoist__find-completed-tasks` only if the user asks for them.
4. Map: `id` = task id, `title` = task content, `body` = description (`""` if none), `author` = creator name, `created` = `addedAt`, `updated` = `updatedAt` (or `addedAt` if absent), `url` = `https://app.todoist.com/app/task/<id>`, metadata `project`, `section`, `priority` (`p1`–`p4`), `labels`, `due`, `recurring`, `deadline`, `completed`, `parentId`, `assignee`.

### Jira — Atlassian MCP
1. `mcp__atlassian__getAccessibleAtlassianResources` once for the `cloudId`.
2. `mcp__atlassian__searchJiraIssuesUsingJql` with a bounded JQL (unbounded queries are rejected), e.g. `created >= "2000-01-01" ORDER BY created ASC` or `project = KAN ORDER BY created ASC`, `maxResults: 100`, `responseContentFormat: "markdown"`, `fields: ["summary","description","status","issuetype","priority","labels","assignee","reporter","creator","created","updated","project","parent","duedate"]`, paging with `nextPageToken`. Large results are saved to a file; read it with `jq`/Python instead of in-context.
3. Map: `id` = issue `key` (e.g. `KAN-4`), `title` = `summary`, `body` = `description` Markdown string (`""` when Jira returns an empty ADF document object instead of a string), `author` = `creator.displayName`, `created` / `updated` = `created` / `updated` **converted to UTC** (`YYYY-MM-DDTHH:MM:SS.mmmZ`), `url` = `webUrl`, metadata `key`, `issueType` (= `issuetype.name`), `status` (= `status.name`), `priority` (= `priority.name` or null), `assignee` / `reporter` (display names or null), `labels`, `project` (= `project.name`), `parent` (= `parent.key` or null), `due` (= `duedate`).

## Step 3 — Write the files

Write files with a small Python script kept in the scratchpad directory (not in `dataExports/`), run with `python3 -I`, that for each new item:

- builds the object with the shared fields in order `service, id, title, body, author, created, updated, url, metadata`;
- computes the filename `<YYYY-MM-DD_HH-MM-SS>_<short-id>.json` from `created` converted to UTC, with the per-service short-id rule from `localStorageFormats.md`;
- writes `json.dumps(item, indent=2, ensure_ascii=False) + "\n"` to `dataExports/<service>/`;
- refuses to overwrite an existing file (`open(path, "x")`).

Never invent values. If the service did not return a field, use `null` (or `[]` for lists) and, if it is a new kind of gap, add it to the "Nullable and approximate fields" table in `localStorageFormats.md`.

## Step 4 — Verify and report

```bash
for f in dataExports/*/*.json; do python3 -I -c "
import json,sys
d=json.load(open(sys.argv[1]))
assert list(d)[:9]==['service','id','title','body','author','created','updated','url','metadata'], sys.argv[1]
" "$f" || echo "BAD $f"; done
ls dataExports/*/ | head -50
```

Also check there are no duplicate `id`s per service. Report per service: new files written, items skipped as already downloaded, total on disk, and any null/approximate fields.

Do not commit or push unless the user asks.
