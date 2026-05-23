# ==============================================================================
# views/player_view.py - Complete Player Management Tab View
# Fixed: Card alignment issues (removed double-padding)
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
    if HISTORY_FILE.exists():
        try: return json.loads(HISTORY_FILE.read_text())
        except Exception: return {}
    return {}

def save_history(history):
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(history, indent=4))
    except Exception: pass

def format_steam_id(uid):
    if not uid: return "Steam ID: N/A"
    return f"Steam ID: {uid[6:]}" if uid.startswith("steam_") else f"Steam ID: {uid}"

class SelectableLabel(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        initial_text = kwargs.pop("text", "")
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("border_width", 0)
        super().__init__(master, **kwargs)
        self.bind("<Button-1>", lambda e: self.focus_set())
        if initial_text:
            self.insert(0, initial_text)
        self.configure(state="readonly")

    def configure(self, require_redraw=False, **kwargs):
        if "text" in kwargs:
            new_text = kwargs.pop("text")
            super().configure(state="normal")
            self.delete(0, "end")
            self.insert(0, new_text)
            super().configure(state="readonly")
        super().configure(require_redraw=require_redraw, **kwargs)

def setup_player_tab(app, tab):
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    housing.add_header("Player Management", "Monitor active sessions and execute moderation commands.")

    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    split_chassis.grid_columnconfigure(0, weight=4, uniform="psplit")
    split_chassis.grid_columnconfigure(1, weight=6, uniform="psplit")

    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    # FIXED: Added padx=0 to align perfectly with the header card above
    dir_card = StandardCard(left_container, title="PLAYER DIRECTORY", icon="👥")
    dir_card.pack(fill="both", expand=True, padx=0)
    
    app.player_list_tabs = ctk.CTkTabview(dir_card, segmented_button_selected_color=COLOR_NEON_BLUE)
    app.player_list_tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    tab_online = app.player_list_tabs.add("Online")
    tab_offline = app.player_list_tabs.add("History")

    app.player_scroll_online = ctk.CTkScrollableFrame(tab_online, fg_color="transparent")
    app.player_scroll_online.pack(fill="both", expand=True)
    app.player_scroll_offline = ctk.CTkScrollableFrame(tab_offline, fg_color="transparent")
    app.player_scroll_offline.pack(fill="both", expand=True)

    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # FIXED: Added padx=0 to align perfectly with the header card above
    mod_card = StandardCard(right_container, title="MODERATION CONTROL", icon="🛡️")
    mod_card.pack(fill="x", padx=0)
    
    sel_inner = InnerCard(mod_card)
    sel_inner.pack(fill="x", padx=15, pady=(0, 15))

    ctk.CTkLabel(sel_inner, text="Selected Profile", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    app.lbl_selected_player = SelectableLabel(sel_inner, text="No Player Selected", font=("Segoe UI", 12, "italic"), text_color="#9CA3AF")
    app.lbl_selected_player.pack(anchor="w", fill="x", padx=20)
    app.lbl_selected_uid = SelectableLabel(sel_inner, text="Steam ID: N/A", font=("JetBrains Mono", 11), text_color="#9CA3AF")
    app.lbl_selected_uid.pack(anchor="w", fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(sel_inner, text="Action Reason:", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=(10, 2))
    app.ent_admin_reason = ctk.CTkEntry(sel_inner, placeholder_text="Reason...", fg_color="#08080A", border_color="#1F2937")
    app.ent_admin_reason.pack(fill="x", padx=20, pady=(0, 20))

    btn_frame = ctk.CTkFrame(sel_inner, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    ctk.CTkButton(btn_frame, text="Kick", fg_color="#FF8C00", text_color="#08080A", font=("Segoe UI", 11, "bold"), command=lambda: app.kick_selected_player()).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ctk.CTkButton(btn_frame, text="Ban", fg_color=COLOR_NEON_PINK, text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), command=lambda: app.ban_selected_player()).pack(side="left", fill="x", expand=True, padx=5)
    ctk.CTkButton(btn_frame, text="Unban", fg_color=COLOR_NEON_BLUE, text_color="#08080A", font=("Segoe UI", 11, "bold"), command=lambda: app.unban_selected_player()).pack(side="left", fill="x", expand=True, padx=(5, 0))

    # FIXED: Added padx=0 for global broadcast alignment
    bc_card = StandardCard(right_container, title="GLOBAL BROADCAST", icon="📢")
    bc_card.pack(fill="x", padx=0)
    bc_inner = InnerCard(bc_card)
    bc_inner.pack(fill="x", padx=15, pady=(0, 15))
    
    app.ent_announcement = ctk.CTkEntry(bc_inner, placeholder_text="Type message...", fg_color="#08080A", border_color="#1F2937")
    app.ent_announcement.pack(side="left", fill="x", expand=True, padx=(15, 8), pady=12)
    ctk.CTkButton(bc_inner, text="SEND", width=80, fg_color="#16161F", border_color=COLOR_NEON_BLUE, border_width=1, text_color=COLOR_NEON_BLUE, command=lambda: app.send_announcement()).pack(side="right", padx=(0, 15))

def update_player_management_list(app, players):
    history = load_history()
    curr_time = time.strftime("%Y-%m-%d %H:%M:%S")
    active_uids = set()
    for p in players:
        uid = p.get("userId", "")
        if uid:
            active_uids.add(uid)
            history[uid] = {"name": p.get("name", "Unknown"), "level": p.get("level", "?"), "last_seen": curr_time}
    save_history(history)
    
    for w in app.player_scroll_online.winfo_children(): w.destroy()
    if not players:
        ctk.CTkLabel(app.player_scroll_online, text="No players online.", font=("Segoe UI", 11, "italic"), text_color="#9CA3AF").pack(pady=20)
    else:
        for p in players:
            name, uid = p.get("name"), p.get("userId")
            btn = ctk.CTkButton(app.player_scroll_online, text=f"{name} (Lvl {p.get('level')})\n{format_steam_id(uid)}", fg_color="#08080A", border_color="#1F2937", border_width=1, command=lambda n=name, u=uid: select_player(app, n, u))
            btn.pack(fill="x", padx=10, pady=4)

    for w in app.player_scroll_offline.winfo_children(): w.destroy()
    offline = {u: d for u, d in history.items() if u not in active_uids}
    for u, d in sorted(offline.items(), key=lambda x: x[1].get("last_seen", ""), reverse=True):
        name = d.get("name")
        btn = ctk.CTkButton(app.player_scroll_offline, text=f"{name} (Lvl {d.get('level')})\nSeen: {d.get('last_seen')}", fg_color="#08080A", border_color="#1F2937", border_width=1, text_color="#9CA3AF", command=lambda n=name, uid=u: select_player(app, n, uid))
        btn.pack(fill="x", padx=10, pady=4)

def select_player(app, name, uid):
    app.selected_player_uid = uid
    app.selected_player_name = name
    app.lbl_selected_player.configure(text=f"Selected: {name}", font=("Segoe UI", 12, "bold"), text_color=COLOR_NEON_BLUE)
    app.lbl_selected_uid.configure(text=format_steam_id(uid), text_color="#E2E8F0")