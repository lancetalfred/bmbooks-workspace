"""
BookKeeper — BMBooks Sync Monitor
Polls bookscan_sync.log every 2s and surfaces status, progress, and per-item
drill-down to Louisa without her needing to open a terminal.
"""

import json
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# ── Paths (all relative to this script's directory) ──────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SYNC_SCRIPT  = os.path.join(BASE_DIR, "bookscan_sync.py")
LOG_FILE     = os.path.join(BASE_DIR, "bookscan_sync.log")
LOCK_FILE    = os.path.join(BASE_DIR, "sync.lock")
SUMMARY_FILE = os.path.join(BASE_DIR, "last_run_summary.json")

# ── Log parsing patterns ──────────────────────────────────────────────────────
RE_CREATED  = re.compile(r"Created\s+\[([^\]]+)\]\s+(.+)")
RE_UPDATED  = re.compile(r"Updated\s+\[([^\]]+)\]\s+(.+)")
RE_ERROR    = re.compile(r"Error\s+\[([^\]]+)\]\s+(.+?)\s+—\s+(.+)")
RE_PROGRESS = re.compile(r"Progress:\s+(\d+)/(\d+)")
RE_STARTED  = re.compile(r"Started:\s+(.+)")
RE_MODE     = re.compile(r"Mode:\s+(.+)")
RE_COMPLETE = re.compile(r"Sync complete")
RE_DETAIL_C = re.compile(r"DETAIL_C\s+\[([^\]]+)\]\s+(.+)")
RE_DETAIL_U = re.compile(r"DETAIL_U\s+\[([^\]]+)\]\s+(.+)")
RE_WARN     = re.compile(r"WARN\s+\[([^\]]+)\]\s+(.+?)\s+\|\|\|\s+(.+)")


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify="left",
                 background="#ffffe0", relief="solid", borderwidth=1,
                 font=("Segoe UI", 8), wraplength=300, padx=6, pady=4).pack()

    def _hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class BookKeeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BookKeeper")
        self.root.resizable(True, True)
        self.root.minsize(600, 420)

        # Session state
        self.created_items       = []
        self.updated_items       = []
        self.error_items         = []
        self.warning_items       = []
        self.progress_max        = 0
        self.last_sync_time      = "—"
        self.sync_mode           = "—"
        self._log_pos            = 0
        self._from_previous_sync = False

        self._build_ui()
        self._load_last_run_summary()
        self._seek_log_to_end()
        self._poll()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        BG = "white"
        self.root.configure(bg=BG)
        pad = {"padx": 12, "pady": 6}

        # Status row
        status_frame = tk.Frame(self.root, bg=BG)
        status_frame.pack(fill="x", **pad)

        help_btn = tk.Button(status_frame, text=" ? ",
                             font=("Segoe UI", 9), fg="#444444",
                             bg="#eeeeee", relief="flat", cursor="hand2",
                             command=self._show_help)
        help_btn.pack(side="right", padx=(0, 4))

        self.status_dot = tk.Label(status_frame, text="●", fg="grey",
                                   font=("Segoe UI", 14), bg=BG)
        self.status_dot.pack(side="left")
        ToolTip(self.status_dot, "Shows whether a sync is running and if anything needs your attention")

        self.status_label = tk.Label(status_frame, text="Up to date",
                                     font=("Segoe UI", 11, "bold"), fg="black", bg=BG)
        self.status_label.pack(side="left", padx=(4, 16))
        ToolTip(self.status_label, "Shows whether a sync is running and if anything needs your attention")

        self.last_sync_label = tk.Label(status_frame, text="Last sync: —",
                                        font=("Segoe UI", 9), fg="#444444", bg=BG)
        self.last_sync_label.pack(side="left")

        # Mode label
        self.mode_label = tk.Label(self.root, text="Mode: —",
                                   font=("Segoe UI", 9), fg="#444444", bg=BG)
        self.mode_label.pack(anchor="w", padx=12)

        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var,
                                            maximum=100)
        self.progress_bar.pack(fill="x", padx=12, pady=(4, 2))
        ToolTip(self.progress_bar, "How far through the current sync we are")

        self.progress_label = tk.Label(self.root, text="",
                                       font=("Segoe UI", 9), fg="#444444", bg=BG)
        self.progress_label.pack(anchor="w", padx=12)

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=12, pady=6)

        # Count buttons (clickable)
        counts_frame = tk.Frame(self.root, bg=BG)
        counts_frame.pack(fill="x", padx=12, pady=2)

        self.created_btn = tk.Button(counts_frame, text="Created: 0",
                                     font=("Segoe UI", 10, "bold"), fg="#2a7a2a",
                                     bg=BG, relief="flat", cursor="hand2",
                                     command=lambda: self._show_detail("Created", self.created_items, ["ISBN", "Title", "Details"]))
        self.created_btn.pack(side="left", padx=(0, 24))
        ToolTip(self.created_btn, "Books added to your Shopify store for the first time in this sync — click to see the list")

        self.updated_btn = tk.Button(counts_frame, text="Updated: 0",
                                     font=("Segoe UI", 10, "bold"), fg="#1a4a8a",
                                     bg=BG, relief="flat", cursor="hand2",
                                     command=lambda: self._show_detail("Updated", self.updated_items, ["ISBN", "Title", "Changed"]))
        self.updated_btn.pack(side="left", padx=(0, 24))
        ToolTip(self.updated_btn, "Books whose details (price, stock, etc.) changed in Bookscan and were refreshed on Shopify — click to see what changed")

        self.warnings_btn = tk.Button(counts_frame, text="Warnings: 0",
                                      font=("Segoe UI", 10, "bold"), fg="#cc6600",
                                      bg=BG, relief="flat", cursor="hand2",
                                      command=lambda: self._show_detail("Warnings", self.warning_items, ["ISBN", "Title", "Issues"]))
        self.warnings_btn.pack(side="left", padx=(0, 24))
        ToolTip(self.warnings_btn, "Products with missing or unusual data in Bookscan — click to see which ones and what to fix")

        self.errors_btn = tk.Button(counts_frame, text="Errors: 0",
                                    font=("Segoe UI", 10, "bold"), fg="#8a1a1a",
                                    bg=BG, relief="flat", cursor="hand2",
                                    command=lambda: self._show_detail("Errors", self.error_items, ["ISBN", "Title", "Reason"]))
        self.errors_btn.pack(side="left")
        ToolTip(self.errors_btn, "Products that couldn't sync due to a technical error — click to see details, then contact Lance if needed")

        tk.Label(counts_frame, text="  ← click to view detail",
                 font=("Segoe UI", 8), fg="#aaa", bg=BG).pack(side="left")

        self.prev_sync_label = tk.Label(self.root, text="",
                                        font=("Segoe UI", 8), fg="#999999", bg=BG)
        self.prev_sync_label.pack(anchor="w", padx=14)

        self.guidance_label = tk.Label(self.root, text="",
                                       font=("Segoe UI", 8, "italic"), fg="#555555", bg=BG)
        self.guidance_label.pack(anchor="w", padx=14)

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=12, pady=6)

        # Activity log
        tk.Label(self.root, text="Activity log:", font=("Segoe UI", 9, "bold"),
                 fg="black", bg=BG).pack(anchor="w", padx=12)

        log_frame = tk.Frame(self.root, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(2, 8))

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(log_frame, height=10, width=72,
                                font=("Consolas", 9), state="disabled",
                                bg="#f0f0f0", fg="black",
                                yscrollcommand=scrollbar.set, wrap="none")
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)
        self.log_text.tag_config("error", foreground="#cc0000")
        self.log_text.tag_config("created", foreground="#2a7a2a")
        self.log_text.tag_config("updated", foreground="#1a4a8a")
        self.log_text.tag_config("detail", foreground="#999999")
        self.log_text.tag_config("warning", foreground="#cc6600")

        # Sync Now button
        self.sync_btn = tk.Button(self.root, text="  Sync Now  ",
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#1A0A2E", fg="white",
                                  relief="flat", cursor="hand2",
                                  padx=16, pady=6,
                                  command=self._sync_now)
        self.sync_btn.pack(pady=(0, 14))
        ToolTip(self.sync_btn, "Run a sync right now instead of waiting for the next scheduled sync")

    # ── Startup — pre-populate from last run summary ──────────────────────────

    def _load_last_run_summary(self):
        if not os.path.exists(SUMMARY_FILE):
            return
        try:
            with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        has_data = any(data.get(k) for k in ("created", "updated", "warnings", "errors"))
        if not has_data:
            return
        for item in data.get("created_items", []):
            self.created_items.append(item)
        for item in data.get("updated_items", []):
            self.updated_items.append(item)
        for item in data.get("warning_items", []):
            self.warning_items.append(item)
        for item in data.get("error_items", []):
            self.error_items.append(item)
        self._from_previous_sync = True
        ts = data.get("completed", "")
        time_part = ts[11:16] if len(ts) >= 16 else ts
        self.prev_sync_label.config(text=f"↑ from previous sync · {time_part}")
        self._refresh_counts()

    # ── Log polling ───────────────────────────────────────────────────────────

    def _seek_log_to_end(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                self._log_pos = f.tell()

    def _poll(self):
        self._read_new_lines()
        self._update_status_dot()
        self.root.after(2000, self._poll)

    def _read_new_lines(self):
        if not os.path.exists(LOG_FILE):
            return
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            f.seek(self._log_pos)
            new_lines = f.readlines()
            self._log_pos = f.tell()

        for raw in new_lines:
            line = raw.strip()
            if not line:
                continue
            self._parse_line(line)
            self._append_log(line)

    def _parse_line(self, line):
        # New sync starting — reset session state
        if RE_STARTED.search(line):
            m = RE_STARTED.search(line)
            self.last_sync_time = m.group(1)
            self.last_sync_label.config(text=f"Last sync: {self.last_sync_time}")
            self.created_items.clear()
            self.updated_items.clear()
            self.error_items.clear()
            self.warning_items.clear()
            self._from_previous_sync = False
            self.prev_sync_label.config(text="")
            self.guidance_label.config(text="")
            self.progress_var.set(0)
            self.progress_label.config(text="")
            self._refresh_counts()
            return

        if RE_MODE.search(line):
            mode = RE_MODE.search(line).group(1)
            display = "Delta sync — only changed products" if "delta" in mode.lower() else mode
            self.sync_mode = display
            self.mode_label.config(text=f"Mode: {display}")
            return

        if m := RE_PROGRESS.search(line):
            current, total = int(m.group(1)), int(m.group(2))
            self.progress_max = total
            pct = int(current / total * 100) if total else 0
            self.progress_var.set(pct)
            self.progress_label.config(text=f"{current:,} / {total:,} products")
            return

        if RE_COMPLETE.search(line):
            self.progress_var.set(100)
            self._refresh_counts()
            return

        if m := RE_CREATED.search(line):
            self.created_items.append([m.group(1), m.group(2), ""])
            self._refresh_counts()
            return

        if m := RE_UPDATED.search(line):
            self.updated_items.append([m.group(1), m.group(2), ""])
            self._refresh_counts()
            return

        if m := RE_ERROR.search(line):
            self.error_items.append((m.group(1), m.group(2), m.group(3)))
            self._refresh_counts()
            return

        if m := RE_WARN.search(line):
            self.warning_items.append((m.group(1), m.group(2), m.group(3)))
            self._refresh_counts()
            return

        if m := RE_DETAIL_C.search(line):
            isbn, detail = m.group(1), m.group(2)
            for item in reversed(self.created_items):
                if item[0] == isbn:
                    item[2] = detail
                    break
            return

        if m := RE_DETAIL_U.search(line):
            isbn, detail = m.group(1), m.group(2)
            for item in reversed(self.updated_items):
                if item[0] == isbn:
                    item[2] = detail
                    break
            return

    def _append_log(self, line):
        # DETAIL lines are parsed for the popup but not shown in the activity log
        if "DETAIL_C" in line or "DETAIL_U" in line:
            return

        tag = None
        if "Error" in line:
            tag = "error"
        elif "WARN" in line:
            tag = "warning"
        elif "Created" in line:
            tag = "created"
        elif "Updated" in line:
            tag = "updated"

        self.log_text.config(state="normal")
        # Extract just the time portion (HH:MM:SS) from the timestamp prefix
        parts = line.split(" ", 2)
        display = f"{parts[1][:8]}  {parts[2]}" if len(parts) >= 3 else line
        self.log_text.insert("end", display + "\n", tag or "")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── UI updates ────────────────────────────────────────────────────────────

    def _refresh_counts(self):
        self.created_btn.config(text=f"Created: {len(self.created_items)}")
        self.updated_btn.config(text=f"Updated: {len(self.updated_items)}")
        self.warnings_btn.config(text=f"Warnings: {len(self.warning_items)}")
        self.errors_btn.config(text=f"Errors: {len(self.error_items)}")
        if len(self.error_items) > 0:
            self.guidance_label.config(text="Something went wrong — check the activity log or contact Lance.")
        elif len(self.warning_items) > 0:
            self.guidance_label.config(text="Fix these in Bookscan — they'll clear on the next sync.")
        else:
            self.guidance_label.config(text="")

    def _update_status_dot(self):
        running      = os.path.exists(LOCK_FILE)
        has_errors   = len(self.error_items) > 0
        has_warnings = len(self.warning_items) > 0

        if running:
            self.status_dot.config(fg="#2a7a2a")
            self.status_label.config(text="Syncing your books to Shopify...")
            self.sync_btn.config(state="disabled")
        else:
            if has_errors:
                colour = "#8a1a1a"
                status_text = "Sync issue — see errors below"
            elif has_warnings:
                colour = "#cc6600"
                status_text = "Up to date — action needed"
            else:
                colour = "grey"
                status_text = "Up to date"
            self.status_dot.config(fg=colour)
            self.status_label.config(text=status_text)
            self.sync_btn.config(state="normal")

    # ── Help popup ────────────────────────────────────────────────────────────

    def _show_help(self):
        win = tk.Toplevel(self.root)
        win.title("BookKeeper — Help")
        win.resizable(False, False)
        win.configure(bg="white")

        content = (
            "What is BookKeeper?\n\n"
            "BookKeeper keeps your Shopify bookshop in sync with your Bookscan catalogue.\n"
            "It runs automatically every hour, checking for new or changed products and\n"
            "updating your website — so you don't have to do anything.\n\n"
            "─────────────────────────────────────\n"
            "Status dot colours\n"
            "─────────────────────────────────────\n"
            "●  Green   — Syncing your books to Shopify right now\n"
            "●  Grey    — Up to date, waiting for the next sync\n"
            "●  Orange  — Up to date, but some products need attention\n"
            "●  Red     — A sync error occurred\n\n"
            "─────────────────────────────────────\n"
            "What the counts mean\n"
            "─────────────────────────────────────\n"
            "Created   — New books added to your Shopify store\n"
            "Updated   — Books whose details changed and were refreshed\n"
            "Warnings  — Products with missing data (e.g. no price, no author)\n"
            "Errors    — Products that couldn't sync due to a technical problem\n\n"
            "Click any count to see the full list.\n\n"
            "─────────────────────────────────────\n"
            "What to do\n"
            "─────────────────────────────────────\n"
            "Warnings  — Fix the issue in Bookscan. It will clear on the next sync.\n"
            "Errors    — Note which books are affected and contact Lance.\n"
            "Nothing   — No action needed. BookKeeper is running on schedule."
        )

        tk.Label(win, text=content, justify="left",
                 font=("Segoe UI", 9), fg="black", bg="white",
                 padx=20, pady=16).pack()

        tk.Button(win, text="  Close  ", command=win.destroy,
                  font=("Segoe UI", 9), bg="#1A0A2E", fg="white",
                  relief="flat", padx=8, pady=4).pack(pady=(0, 16))

        win.geometry("460x520")

    # ── Sync Now ──────────────────────────────────────────────────────────────

    def _sync_now(self):
        if os.path.exists(LOCK_FILE):
            messagebox.showinfo("Sync in progress",
                                "A sync is already running.\nPlease wait for it to finish.")
            return
        subprocess.Popen([sys.executable, SYNC_SCRIPT, "--once"],
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

    # ── Detail popup ──────────────────────────────────────────────────────────

    def _show_detail(self, title, items, columns):
        if not items:
            messagebox.showinfo(title, f"No {title.lower()} items in the current session.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"{title} — {len(items)} items")
        win.resizable(True, True)

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        vsb = tk.Scrollbar(frame, orient="vertical")
        hsb = tk.Scrollbar(frame, orient="horizontal")

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        col_widths = {"ISBN": 130, "Title": 260, "Details": 400, "Changed": 360, "Issues": 300, "Reason": 300}
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 200), minwidth=80)

        def _refresh_tree():
            tree.delete(*tree.get_children())
            for row in items:
                tree.insert("", "end", values=row)
            if win.winfo_exists():
                win.after(2000, _refresh_tree)

        _refresh_tree()

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        win.geometry(f"{sum(col_widths.get(c, 200) for c in columns) + 40}x400")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookKeeperApp(root)
    root.mainloop()
