---
sidebar_position: 3
---

# Shop Machine Setup

This is the one-time setup guide for getting BookKeeper running on the shop machine. You'll need Chrome Remote Desktop access to the shop machine to complete this — roughly 20 minutes start to finish.

:::info Current status — May 25, 2026
Steps 1–6 complete. Python 3.14.4 installed, ~34,500 products synced to Shopify (Draft). Files currently at `C:\BookKeeper\` — move to `Z:\BookKeeper\` before deploying GUI (Step 7). Steps 7 and 8 pending.
:::

---

## What you'll need

- Chrome Remote Desktop access to the shop machine (coordinate with Belinda)
- The `bookscan_sync.py` script and `requirements.txt`
- The Shopify live store access token (from Shopify Admin → Apps → Develop apps → BookKeeper)

---

## Step 1 — Install Python

1. On the shop machine, open a web browser and go to **python.org/downloads**
2. Click **Download Python 3.x** (the big yellow button — latest stable version)
3. Run the installer
4. **Important:** On the first screen of the installer, tick **"Add Python to PATH"** before clicking Install
5. Click **Install Now**
6. When it finishes, click **Close**

**Verify it worked:** Open Command Prompt (search "cmd" in the Start menu) and type:
```
python --version
```
You should see something like `Python 3.12.x`. If you see an error, the PATH wasn't set — reinstall and make sure to tick that box.

---

## Step 2 — Copy the script files

Create the BookKeeper folder on the **Z: drive** (the same drive Bookscan uses) so files are preserved if the PC is replaced:
```
Z:\BookKeeper\
```

Copy these files into that folder:
- `bookscan_sync.py`
- `bookkeeper_gui.py`
- `requirements.txt`

:::tip Why Z: and not C:?
Z: is a mapped network drive connected to the Bookscan server. Files there survive a PC failure or replacement. C: is local to the shop PC.
:::

---

## Step 3 — Install dependencies

1. Open Command Prompt
2. Navigate to the BookKeeper folder:
```
cd C:\BookKeeper
```
3. Install the required packages:
```
pip install -r requirements.txt
```
This downloads and installs three small packages (`dbfread`, `requests`, `schedule`). It only needs to be done once.

---

## Step 4 — Update the script configuration

Open `bookscan_sync.py` in Notepad (right-click → Open with → Notepad) and update these lines near the top of the file:

| Line | Change to |
|---|---|
| `SHOPIFY_STORE_URL` | `"bruce-mckenzie-booksellers.myshopify.com"` |
| `SHOPIFY_ACCESS_TOKEN` | The live store token from Shopify Admin |
| `MAX_PRODUCTS` | `None` |

`DBF_BASE_PATH` auto-detects `Z:\bookscan` — no change needed if the Z: drive is mapped.

Save the file.

---

## Step 5 — Run a dry run to verify everything works

In Command Prompt, run:
```
python C:\BookKeeper\bookscan_sync.py --dry-run
```

You should see the script load the Bookscan files and list the first 20 books it would sync. If it says approximately 38,000 products found, everything is working correctly.

If you see any errors at this point, check the [Troubleshooting](../troubleshooting) guide before going further.

---

## Step 6 — Run the first full sync

This will sync all ~38,000 books to the live Shopify store. It will take several hours on the first run — that's normal.

```
python C:\BookKeeper\bookscan_sync.py
```

You can watch the progress in the Command Prompt window. When it finishes, check Shopify Admin → Products to confirm the books are there.

:::tip
The first sync can be run overnight. You don't need to watch it.
:::

---

## Step 7 — Set up the BookKeeper GUI

The BookKeeper GUI (`bookkeeper_gui.py`) replaces the old `Sync Now.bat` command-line approach. It gives Louisa a simple window showing sync status, progress, and a Sync Now button — no terminal required.

**7a — Copy `Sync Now.bat` to Louisa's desktop**

The file is already in `Z:\BookKeeper\Sync Now.bat`. Right-click it → **Create shortcut** → move the shortcut to the Desktop. (Or copy `Sync Now.bat` directly to the Desktop — either works.)

Contents of `Sync Now.bat`:
```batch
@echo off
cd /d Z:\BookKeeper
python bookkeeper_gui.py
pause
```

**7b — Verify it opens**

Double-click `Sync Now` on the desktop. The BookKeeper window should open showing:
- Status dot (grey = idle, green = running)
- Sync mode label ("Delta sync — only changed products")
- Progress bar
- Created / Updated / Errors counts (click any to see the full ISBN list)
- **Sync Now** button

**7c — Test Sync Now**

Click **Sync Now**. The status dot should turn green and the progress bar should begin moving. Click it again while running — it should show "Sync already in progress."

---

## Step 8 — Set up automatic 2-hour syncs via Task Scheduler

This makes the sync run automatically every 2 hours in the background, without anyone needing to do anything.

1. Open **Task Scheduler** (search for it in the Start menu)
2. Click **Create Basic Task** in the right panel
3. Name it: `BookKeeper Sync`
4. Description: `Syncs Bookscan products to Shopify every 2 hours`
5. Click Next → choose **Daily**
6. Set start time to a convenient time (e.g. 8:00 AM)
7. Click Next → choose **Repeat task every: 2 hours** for a duration of **Indefinitely**
8. Click Next → choose **Start a program**
9. Program/script: `python`
10. Add arguments: `Z:\BookKeeper\bookscan_sync.py --once`
11. Click Finish

**Verify it's working:** Right-click the task → Run. Check `C:\BookKeeper\bookscan_sync.log` to confirm a run was triggered.

---

## What runs automatically vs manually

| Action | How it runs |
|---|---|
| Regular sync (every 2 hours) | Automatic via Task Scheduler |
| Force full refresh | Manual: `python bookscan_sync.py --full` |
| Dry run / check | Manual: `python bookscan_sync.py --dry-run` |
| Check last run time | Open `Z:\BookKeeper\sync_state.json` |
| Check for errors | Open `Z:\BookKeeper\bookscan_sync.log` (or click Errors count in the GUI) |
