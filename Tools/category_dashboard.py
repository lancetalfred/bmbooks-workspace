#!/usr/bin/env python3
"""Category management dashboard server. Proxies Shopify API calls and serves the HTML dashboard."""

import csv
import json
import os
import sys
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

STORE_URL = "bruce-mckenzie-booksellers.myshopify.com"
API_VERSION = "2024-10"
PORT = 8888

SCRIPT_DIR = Path(__file__).parent
CSV_PATH = SCRIPT_DIR.parent / "Reports" / "category_audit.csv"
HTML_PATH = SCRIPT_DIR / "category_dashboard.html"


def get_token():
    token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
    if not token:
        print("ERROR: SHOPIFY_ACCESS_TOKEN environment variable not set.")
        print("Run:  export SHOPIFY_ACCESS_TOKEN='shpat_...'")
        sys.exit(1)
    return token


def parse_audit_csv():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def fetch_collections(token):
    query = """{
      collections(first: 250) {
        edges { node {
          id title handle
          productsCount { count }
          ruleSet { appliedDisjunctively rules { column relation condition } }
        } }
      }
    }"""
    url = f"https://{STORE_URL}/admin/api/{API_VERSION}/graphql.json"
    data = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


class DashboardHandler(BaseHTTPRequestHandler):
    token = None

    def do_GET(self):
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/audit":
            self._serve_json(parse_audit_csv())
        elif self.path == "/api/collections":
            self._serve_json(fetch_collections(self.token))
        else:
            self.send_error(404)

    def _serve_html(self):
        content = HTML_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)

    def _serve_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    token = get_token()
    DashboardHandler.token = token
    server = HTTPServer(("localhost", PORT), DashboardHandler)
    print(f"Category Dashboard running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
