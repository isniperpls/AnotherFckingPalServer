# ==============================================================================
# views/player_view.py
# Player Management View Module
# ==============================================================================

import json
import time
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

HISTORY_FILE = Path("configs/player_history.json")

def load_history():
    """Loads previously connected players from the JSON database."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_history(history):
    """Saves player history to local JSON storage."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history, indent=4))
    except Exception:
        pass

def format_steam_id(uid):
    """Cleanly formats Steam ID by removing 'steam_' prefix."""
    if not uid:
        return "Steam ID: N/A"
    if uid.startswith("steam_"):
        return f"Steam ID: {uid[6:]}"
    return f"Steam ID: {uid}"

class SelectableLabel(ctk.CTkEntry):
    """Custom selectable read-only Entry widget styled like a CTkLabel."""
    def __init__(self, master, **kwargs):
        initial_text = kwargs.pop("text", "")
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("border_width", 0)
        super().__init__(master, **kwargs)
        try:
            self._entry.configure(insertwidth=0)
        except Exception:
            pass
        self.bind("<Button-1>", lambda e: self.focus_set())
        if initial_text:
            self.insert(0, initial_text)
        self.configure(state="readonly")
        self.bind("<Button-3>", self.show_copy_menu)
        self.bind("<Button-2>", self.show_copy_menu)

    def configure(self, require_redraw=False, **kwargs):
        if "text" in kwargs:
            new_text = kwargs.pop("text")
            current_state = self.cget("state")
            super().configure(state="normal")
            self.delete(0, "end")
            self.insert(0, new_text)
            super().configure(state=current_state)
        super().configure(require_redraw=require_redraw, **kwargs)

    def show_copy_menu(self, event):
        self.focus_set()
        menu = tk.Menu(self, tearoff=0, background="#101014", foreground="#E2E8F0", activebackground=COLOR_NEON_BLUE, activeforeground="#08080A", bd=1)
        def copy_text():
            try:
                text = self.selection_get()
            except Exception:
                text = self.get()
            self.clipboard_clear()
            self.clipboard_append(text)
        menu.add_command(label="Copy", command=copy_text)
        menu.tk_popup(event.x_root, event.y_root)

def export_player_roster(app):
    """Exports player history to a structured text file."""
    history = load_history()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile="player_roster.txt", title="Export Player Roster")
    if not file_path:
        return
    try:
        online_uids = getattr(app, "online_uids_cache", set())
        lines = ["=" * 85, "                       PLAYER ROSTER", "=" * 85, f"Export Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"]
        lines.append(f"{'STATUS':<8} | {'PLAYER NAME':<20} | {'LEVEL':<6} | {'STEAM ID':<20} | {'LAST ONLINE':<20}")
        lines.append("-" * 85)
        sorted_players = []
        for uid, data in history.items():
            sorted_players.append({"uid": uid, "name": data.get("name", "Unknown"), "level": data.get("level", "?"), "last_seen": data.get("last_seen", "Unknown"), "online": uid in online_uids})
        sorted_players.sort(key=lambda x: (not x["online"], x["name"].lower()))
        for p in sorted_players:
            status = "ONLINE" if p["online"] else "OFFLINE"
            lines.append(f"{status:<8} | {p['name']:<20} | {p['level']:<6} | {p['uid']:<20} | {p['last_seen']:<20}")
        Path(file_path).write_text("\n".join(lines), encoding="utf-8")
        messagebox.showinfo("Success", "Roster exported successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def setup_player_tab(app, tab):
    """Constructs player directory tabs and moderation tools."""
    app.online_uids_cache = set()
    
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    # Title Card Header
    housing.add_header("Player Management", "Monitor active sessions, review historical data, and execute administrative moderation.")

    # Wrapper frame to avoid grid/pack conflict inside housing container
    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)

    split_chassis.grid_columnconfigure(0, weight=45, uniform="player_split")
    split_chassis.grid_columnconfigure(1, weight=55, uniform="player_split")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: PLAYER DIRECTORY
    # --------------------------------------------------------------------------
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    dir_card = StandardCard(left_container, title="PLAYER DIRECTORY", icon="👥")
    dir_card.pack(fill="both", expand=True, padx=0)
    
    app.player_list_tabs = ctk.CTkTabview(dir_card, segmented_button_selected_color=COLOR_NEON_BLUE, text_color="#E2E8F0")
    app.player_list_tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    tab_online = app.player_list_tabs.add("Online")
    tab_offline = app.player_list_tabs.add("History")

    app.player_scroll_online = ctk.CTkScrollableFrame(tab_online, fg_color="transparent", scrollbar_button_color="#2B2B2B", scrollbar_button_hover_color="#2B2B2B", scrollbar_fg_color="transparent")
    app.player_scroll_online.pack(fill="both", expand=True)

    app.player_scroll_offline = ctk.CTkScrollableFrame(tab_offline, fg_color="transparent", scrollbar_button_color="#2B2B2B", scrollbar_button_hover_color="#2B2B2B", scrollbar_fg_color="transparent")
    app.player_scroll_offline.pack(fill="both", expand=True)

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: MODERATION & BROADCAST
    # --------------------------------------------------------------------------
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # Moderation Card
    mod_card = StandardCard(right_container, title="MODERATION CONTROL", icon="🛡️")
    mod_card.pack(fill="x", padx=0)
    
    app.selected_card = InnerCard(mod_card)
    app.selected_card.pack(fill="x", padx=15, pady=(0, 15))

    ctk.CTkLabel(app.selected_card, text="Selected Player Profile", font=("Segoe UI", 12, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=20, pady=(15, 5))
    app.lbl_selected_player = SelectableLabel(app.selected_card, text="No Player Selected", font=("Segoe UI", 12, "italic"), text_color="#9CA3AF")
    app.lbl_selected_player.pack(anchor="w", fill="x", padx=20, pady=2)
    app.lbl_selected_uid = SelectableLabel(app.selected_card, text="Steam ID: N/A", font=("JetBrains Mono", 11), text_color="#9CA3AF")
    app.lbl_selected_uid.pack(anchor="w", fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(app.selected_card, text="Action Reason:", font=("Segoe UI", 11), text_color="#E2E8F0").pack(anchor="w", padx=20, pady=(10, 2))
    app.ent_admin_reason = ctk.CTkEntry(app.selected_card, placeholder_text="Reason...", fg_color="#08080A", border_color="#1F2937", text_color="#E2E8F0")
    app.ent_admin_reason.pack(fill="x", padx=20, pady=(0, 20))

    # Action Buttons
    btn_frame = ctk.CTkFrame(app.selected_card, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=(0, 20))
    btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

    app.btn_kick_selected = ctk.CTkButton(btn_frame, text="Kick", fg_color="#FF8C00", text_color="#08080A", font=("Segoe UI", 11, "bold"), command=app.kick_selected_player)
    app.btn_kick_selected.grid(row=0, column=0, padx=(0, 3), sticky="ew")
    app.btn_ban_selected = ctk.CTkButton(btn_frame, text="Ban", fg_color=COLOR_NEON_PINK, text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), command=app.ban_selected_player)
    app.btn_ban_selected.grid(row=0, column=1, padx=(3, 3), sticky="ew")
    app.btn_unban_selected = ctk.CTkButton(btn_frame, text="Unban", fg_color=COLOR_NEON_BLUE, text_color="#08080A", font=("Segoe UI", 11, "bold"), command=app.unban_selected_player)
    app.btn_unban_selected.grid(row=0, column=2, padx=(3, 0), sticky="ew")

    # Broadcast Card
    bc_card = StandardCard(right_container, title="GLOBAL BROADCAST", icon="📢")
    bc_card.pack(fill="x", padx=0)
    
    bc_inner = InnerCard(bc_card)
    bc_inner.pack(fill="x", padx=15, pady=(0, 15))
    
    app.ent_announcement = ctk.CTkEntry(bc_inner, placeholder_text="Type message...", height=32, fg_color="#08080A", border_color="#1F2937", text_color="#E2E8F0")
    app.ent_announcement.pack(side="left", fill="x", expand=True, padx=(15, 8), pady=12)
    app.btn_announce = ctk.CTkButton(bc_inner, text="SEND", width=80, height=32, fg_color="#16161F", border_color=COLOR_NEON_BLUE, border_width=1, text_color=COLOR_NEON_BLUE, command=app.send_announcement)
    app.btn_announce.pack(side="right", padx=(0, 15), pady=12)

    # --------------------------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------------------------
    housing.footer.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
    
    ctk.CTkLabel(
        housing.footer,
        text="📝 Exports a formatted text file containing the complete history of all connected players.",
        font=("Segoe UI", 11, "italic"),
        text_color="#9CA3AF"
    ).pack(side="left", padx=20, pady=12)

    app.btn_export_roster = ctk.CTkButton(
        housing.footer,
        text="EXPORT PLAYER ROSTER",
        height=36,
        width=240,
        fg_color=COLOR_NEON_BLUE,
        hover_color="#00B4CC",
        text_color="#08080A",
        font=("Segoe UI", 12, "bold"),
        command=lambda: export_player_roster(app)
    )
    app.btn_export_roster.pack(side="right", padx=15, pady=10)

def select_player(app, name, uid):
    app.selected_player_uid = uid
    app.selected_player_name = name
    app.lbl_selected_player.configure(text=f"Selected: {name}", font=("Segoe UI", 12, "bold"), text_color=COLOR_NEON_BLUE)
    app.lbl_selected_uid.configure(text=format_steam_id(uid), text_color="#E2E8F0")

def update_player_management_list(app, players):
    history = load_history()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    active_uids = set()
    for p in players:
        uid = p.get("userId", "")
        if uid:
            active_uids.add(uid)
            history[uid] = {"name": p.get("name", "Unknown"), "level": p.get("level", "?"), "last_seen": current_time}
    save_history(history)
    for w in app.player_scroll_online.winfo_children(): w.destroy()
    if not players:
        ctk.CTkLabel(app.player_scroll_online, text="No players online.", font=("Segoe UI", 11, "italic"), text_color="#9CA3AF").pack(pady=20)
    else:
        for p in players:
            btn = ctk.CTkButton(app.player_scroll_online, text=f"{p.get('name')} (Lvl {p.get('level')})\n{format_steam_id(p.get('userId'))}", fg_color="#08080A", border_color="#1F2937", border_width=1, text_color="#E2E8F0", command=lambda n=p.get("name"), u=p.get("userId"): select_player(app, n, u))
            btn.pack(fill="x", padx=10, pady=4)
    for w in app.player_scroll_offline.winfo_children(): w.destroy()
    offline = {u: d for u, d in history.items() if u not in active_uids}
    for u, d in sorted(offline.items(), key=lambda x: x[1].get("last_seen", ""), reverse=True):
        btn = ctk.CTkButton(app.player_scroll_offline, text=f"{d.get('name')} (Lvl {d.get('level')})\nSeen: {d.get('last_seen')}", fg_color="#08080A", border_color="#1F2937", border_width=1, text_color="#9CA3AF", command=lambda n=d.get("name"), uid=u: select_player(app, n, uid))
        btn.pack(fill="x", padx=10, pady=4)