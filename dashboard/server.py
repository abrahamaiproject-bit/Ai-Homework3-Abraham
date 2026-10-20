#!/usr/bin/env python3
"""Local dashboard server for the JSON files in ../dataExports.

Serves index.html and a single API endpoint, /api/items, which returns every
exported item from all services. Files are re-read on each request, so newly
exported data shows up after a browser refresh. Nothing here talks to the
live services.
"""

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
DATA_DIR = DASHBOARD_DIR.parent / "dataExports"
SERVICES = ["gmail", "github", "notion", "linear", "todoist", "jira"]


def load_items():
    items = []
    for service in SERVICES:
        folder = DATA_DIR / service
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as err:
                print(f"Skipping {path}: {err}")
                continue
            item.setdefault("service", service)
            item["file"] = f"{service}/{path.name}"
            items.append(item)
    items.sort(key=lambda i: i.get("created") or "", reverse=True)
    return items


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/items":
            body = json.dumps(load_items(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/", "/index.html"):
            self.path = "/index.html"
            super().do_GET()
        else:
            self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Reading data from {DATA_DIR}")
    print(f"Dashboard running at http://{args.host}:{args.port}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
