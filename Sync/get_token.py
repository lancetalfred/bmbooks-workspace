"""
One-time script to get a permanent Shopify offline access token for the live store.
Run this, authorize in the browser, and copy the printed token to bookscan_sync.py.
"""
import os
import threading
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json

CLIENT_ID     = os.environ["SHOPIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SHOPIFY_CLIENT_SECRET"]
STORE         = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
REDIRECT_URI  = "http://localhost:8080/callback"
SCOPES        = "write_products,read_products,write_inventory,read_inventory,read_locations"

token_result = []

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if code:
            # Exchange code for offline token
            url = f"https://{STORE}/admin/oauth/access_token"
            data = json.dumps({
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            }).encode()
            req = urllib.request.Request(url, data=data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            access_token = result.get("access_token", "ERROR")
            token_result.append(access_token)
            self.wfile.write(b"<h2>Token retrieved! You can close this tab.</h2>")
        else:
            self.wfile.write(b"<h2>Error: no code received.</h2>")

        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass  # suppress server logs


if __name__ == "__main__":
    auth_url = (
        f"https://{STORE}/admin/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state=bmbooks"
        f"&grant_options[]=offline"
    )

    print("Opening browser for Shopify authorization...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.serve_forever()

    if token_result:
        print("\n" + "="*60)
        print("SUCCESS — copy this token into bookscan_sync.py:")
        print(f"\nSHOPIFY_ACCESS_TOKEN = \"{token_result[0]}\"\n")
        print("="*60)
    else:
        print("No token received.")
