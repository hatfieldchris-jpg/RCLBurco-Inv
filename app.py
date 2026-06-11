import os
import io
import re
import requests
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

# ---------------------------------------------------------------------------
# OneDrive share-link helper
# ---------------------------------------------------------------------------

def build_download_url(share_url: str) -> str:
    """
    Convert a standard OneDrive share link into a direct-download URL.
    Works for both personal (onedrive.live.com) and business (sharepoint.com) links.
    """
    # Business / SharePoint share links — append ?download=1
    if "sharepoint.com" in share_url or "my.sharepoint.com" in share_url:
        sep = "&" if "?" in share_url else "?"
        return share_url + sep + "download=1"

    # Personal OneDrive — convert the resid/id style share link
    # e.g. https://1drv.ms/x/s!Axxx  or  https://onedrive.live.com/...
    if "1drv.ms" in share_url:
        # Follow the short link to get the real URL
        r = requests.head(share_url, allow_redirects=True, timeout=10)
        share_url = r.url

    # onedrive.live.com share link → direct download
    if "onedrive.live.com" in share_url:
        return re.sub(r"redir\?", "download?", share_url)

    # Fallback: just append download=1
    sep = "&" if "?" in share_url else "?"
    return share_url + sep + "download=1"


EXPECTED_COLUMNS = [
    "Burco #",
    "SCN",
    "Description",
    "UOM",
    "Qty On Hand",
    "Qty On Order with Supplier",
    "Supplier",
]


def load_inventory() -> list[dict]:
    share_url    = os.environ["ONEDRIVE_SHARE_URL"]
    download_url = build_download_url(share_url)

    resp = requests.get(download_url, timeout=30)
    resp.raise_for_status()

    df = pd.read_excel(io.BytesIO(resp.content), engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    present = [c for c in EXPECTED_COLUMNS if c in df.columns]
    df = df[present]

    if "Description" in df.columns:
        df = df.sort_values("Description", key=lambda s: s.str.lower(), ignore_index=True)

    df = df.fillna("")
    return df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/inventory")
def inventory():
    try:
        data = load_inventory()
        return jsonify({"status": "ok", "data": data})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
