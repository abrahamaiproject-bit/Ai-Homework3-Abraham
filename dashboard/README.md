# Data Exports Dashboard

A small local website for searching the data exported into `../dataExports/`
(Gmail, GitHub, Notion, Linear, Todoist and Jira). It only reads the local JSON files — it never
connects to the live services.

## Requirements

- Python 3.8 or newer (standard library only, nothing to install)

## Run it

From the repository root:

```bash
python3 dashboard/server.py
```

Then open **http://127.0.0.1:8765/** in your browser. Stop the server with `Ctrl+C`.

Options:

```bash
python3 dashboard/server.py --port 9000        # use a different port
```

The JSON files are re-read on every page load, so after exporting new data just
refresh the browser.

## Features

- **Search** — one box searches title, body and metadata of every item across all
  services. Multiple words must all match (case-insensitive).
- **Service filters** — show All, Gmail, GitHub, Notion, Linear, Todoist or Jira. Each button shows
  how many items match the current search.
- **Results** — each result shows a colored badge with the service name, the title,
  the date, a text snippet with the search terms highlighted, and a link to the
  original item. If a term only matches metadata, the matching metadata fields are
  shown instead.
- **Full item view** — click a result to see its full body, author/dates and all
  metadata. Close with `×`, `Esc` or by clicking outside.

## Files

| File | Purpose |
|---|---|
| `server.py` | Serves `index.html` and `GET /api/items` (all items from `dataExports/*/*.json`, newest first) |
| `index.html` | The whole UI: search, filters, results and detail view |
