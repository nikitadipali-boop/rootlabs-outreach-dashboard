# Deploy Guide - Streamlit Cloud

Follow these steps once. After that, every push to GitHub auto-updates the live dashboard.

---

## Step 1 - Create a GitHub repository

1. Go to https://github.com/new
2. Repository name: `rootlabs-outreach-dashboard`
3. Set to **Private**
4. Do NOT tick "Add a README" (repo must be empty)
5. Click **Create repository**
6. GitHub will show you a page with setup commands. Copy the repo URL - it looks like:
   `https://github.com/YOUR_USERNAME/rootlabs-outreach-dashboard.git`

---

## Step 2 - Push the local repo to GitHub

Open Terminal, paste these commands (replace YOUR_USERNAME):

```bash
cd ~/Desktop/apollo-analytics/airtable-visibility-tracker
git remote add origin https://github.com/YOUR_USERNAME/rootlabs-outreach-dashboard.git
git push -u origin main
```

Enter your GitHub username and password when prompted.
(If GitHub asks for a token instead of password: go to GitHub > Settings > Developer Settings > Personal Access Tokens > Generate new token, tick "repo" scope, use that as your password)

---

## Step 3 - Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub (same account)
3. Click **New app**
4. Fill in:
   - **Repository:** `YOUR_USERNAME/rootlabs-outreach-dashboard`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
5. Click **Advanced settings**
6. Under **Secrets**, paste this exactly:
   ```toml
   AIRTABLE_TOKEN = "pat0aSErPoCgOSR2B.4bde5ea5bcf124ac0680d144183be4baf5d158be0d19777e8a4fc7dd43037fa8"
   ```
7. Click **Save** then **Deploy**

Live URL:
**https://rootlabs-outreach-dashboard-andnfravburjolrptdgym3.streamlit.app**

Bookmark that URL. It is accessible from any device, any browser - phone included.

---

## Step 4 - Keep data up to date (daily run)

Snapshots and changelog are stored locally only (not in GitHub).
Run this once a day - the cloud dashboard pulls live from Airtable on every page load,
and the local files build up your historical trend data over time.

```bash
cd ~/Desktop/apollo-analytics/airtable-visibility-tracker
python3 daily_tracker.py
```

The cloud dashboard's Refresh button also pulls fresh data directly from Airtable
without needing a script run.

---

## Running locally (no internet needed)

```bash
/Users/mosaic/Library/Python/3.9/bin/streamlit run ~/Desktop/apollo-analytics/airtable-visibility-tracker/dashboard.py
```

Open http://localhost:8501

---

## File map

```
airtable-visibility-tracker/
  dashboard.py          <- Streamlit app (the dashboard)
  daily_tracker.py      <- Run daily to capture changes
  requirements.txt      <- Python packages (Streamlit Cloud reads this)
  .gitignore            <- Keeps secrets.toml out of GitHub
  .streamlit/
    secrets.toml        <- Local secrets (NOT pushed to GitHub)
  snapshots/
    snapshot_YYYY-MM-DD.json   <- One per day, builds history
  changelog.csv         <- Every state transition ever detected
  daily_summary.xlsx    <- Excel version (local only)
```

---

## Security note

The `.streamlit/secrets.toml` file is listed in `.gitignore` so it will never be
pushed to GitHub. The Airtable token is stored securely in Streamlit Cloud's
secrets manager instead.
