# Burco Inventory App

A mobile-friendly, read-only inventory viewer that pulls live data from an Excel file shared via OneDrive. No Azure, no credentials — just a share link.

---

## Project Structure

```
inventory-app/
├── app.py              # Flask backend — downloads Excel via OneDrive share link
├── requirements.txt    # Python dependencies
├── Procfile            # Render start command
├── render.yaml         # Render deployment config
├── .gitignore
└── static/
    └── index.html      # Mobile-friendly frontend (search + CSV export)
```

---

## Step 1 — Share your Excel file on OneDrive

1. Open **OneDrive** in your browser and locate your inventory Excel file
2. Right-click the file → **Share**
3. Click **"Anyone with the link can view"** (do NOT require sign-in)
4. Click **Copy link**
5. Save that link — you'll need it in Step 3

> ✅ The file stays on your OneDrive. You keep editing it normally.  
> ✅ The link only allows viewing — no one can edit through this link.  
> ✅ Every time the app loads, it fetches a fresh copy automatically.

---

## Step 2 — Push to GitHub

```bash
cd inventory-app
git init
git add .
git commit -m "Initial commit"
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/burco-inventory.git
git push -u origin main
```

---

## Step 3 — Deploy on Render

1. Go to https://render.com → **New** → **Web Service**
2. Connect your GitHub account and select the `burco-inventory` repo
3. Render will detect the settings from `render.yaml` automatically
4. Under **Environment Variables**, add **one** variable:

| Key | Value |
|-----|-------|
| `ONEDRIVE_SHARE_URL` | The share link you copied in Step 1 |

5. Click **Create Web Service**
6. Your app will be live at a URL like `https://burco-inventory.onrender.com`

---

## Excel File Requirements

Your spreadsheet must have these exact column headers in row 1:

| Burco # | SCN | Description | UOM | Qty On Hand | Qty On Order with Supplier | Supplier |

- Column order doesn't matter
- Extra columns are ignored
- Data is sorted alphabetically by **Description** automatically
- Every page load fetches a fresh copy — just save your Excel file and the app reflects changes instantly

---

## Features

- 🔍 **Search** — filters across all columns in real time
- 📤 **Export CSV** — downloads currently visible rows (respects active search)
- 🔄 **Refresh** — re-fetches from OneDrive on demand
- 📱 **Mobile-friendly** — responsive layout, sticky header, touch scroll
- 🔒 **Read-only** — no edit capability exposed

---

## Updating Your Inventory

Edit and save your Excel file in OneDrive as usual. The next time the app is opened or refreshed, it will show the latest data. No redeployment needed.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not load inventory" on first load | Double-check the share link allows anyone to view without sign-in |
| Columns show as blank | Make sure your Excel headers exactly match the expected column names |
| Old data showing | Click the **Refresh** button — or check the file was saved in OneDrive |
