import os
import io
import re
import requests
import openpyxl
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
    if "sharepoint.com" in share_url or "my.sharepoint.com" in share_url:
        sep = "&" if "?" in share_url else "?"
        return share_url + sep + "download=1"

    if "1drv.ms" in share_url:
        r = requests.head(share_url, allow_redirects=True, timeout=10)
        share_url = r.url

    if "onedrive.live.com" in share_url:
        return re.sub(r"redir\?", "download?", share_url)

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

    wb = openpyxl.load_workbook(io.BytesIO(resp.content), data_only=True, read_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)

    # Read header row
    header = [str(c).strip() if c is not None else "" for c in next(rows_iter)]

    # Map column name -> index
    col_index = {name: idx for idx, name in enumerate(header)}
    present_cols = [c for c in EXPECTED_COLUMNS if c in col_index]

    records = []
    for row in rows_iter:
        # Skip completely empty rows
        if row is None or all(v is None for v in row):
            continue

        record = {}
        for col in present_cols:
            idx = col_index[col]
            val = row[idx] if idx < len(row) else None
            record[col] = "" if val is None else val
        records.append(record)

    wb.close()

    # Sort by Description (case-insensitive)
    if "Description" in present_cols:
        records.sort(key=lambda r: str(r.get("Description", "")).lower())

    return records


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
