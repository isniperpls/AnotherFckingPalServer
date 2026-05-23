# ==============================================================================
# views/backups_view.py
# Backups View Module - Restored Split View + Corrected Header
# ==============================================================================

import customtkinter as ctk
import tkinter.messagebox as messagebox
from core.backup_manager import BackupManager
from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

def setup_backups_tab(app, tab):
    """Sets up the scrollable grid layout and list panels for world saves management."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    header_card = housing.add_header(
        "World Backup Manager", 
        "Safely compress, list, delete, and restore Palworld world save states."
    )

    # 1. Action Buttons - Placed in Header
    header_btn_frame = ctk.CTkFrame(header_card, fg_color="transparent")
    header_btn_frame.place(relx=1.0, rely=0.35, anchor="e", x=-25)

    app.btn_change_backup_path = ctk.CTkButton(
        header_btn_frame, 
        text="CHANGE PATH", 
        width=160, 
        height=32,
        fg_color="#16161F",
        hover_color="#1F2937",
        border_color="#1F2937",
        border_width=1,
        text_color="#E2E8F0",
        font=("Segoe UI", 11, "bold"),
        command=app.browse_backup_path
    )
    app.btn_change_backup_path.pack(side="left", padx=(0, 10))

    app.btn_trigger_backup = ctk.CTkButton(
        header_btn_frame, 
        text="CREATE SNAPSHOT", 
        width=160, 
        height=32,
        fg_color=COLOR_NEON_BLUE, 
        hover_color="#00B4CC", 
        text_color="#08080A",
        font=("Segoe UI", 11, "bold"),
        command=app.trigger_manual_backup
    )
    app.btn_trigger_backup.pack(side="left")

    # 2. Path Label - Placed in Header
    app.lbl_backup_path_val = ctk.CTkLabel(
        header_card, 
        text=f"Current Path: {str(app.backup_dir) if app.backup_dir else 'Default (Saved_Backups)'}",
        font=("JetBrains Mono", 10),
        text_color=COLOR_NEON_BLUE
    )
    app.lbl_backup_path_val.place(relx=1.0, rely=0.75, anchor="e", x=-25)

    # 3. Split View Chassis
    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    
    split_chassis.grid_columnconfigure(0, weight=4, uniform="backups")
    split_chassis.grid_columnconfigure(1, weight=6, uniform="backups")

    # 4. LEFT COLUMN: CONFIGURATION
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    config_card = StandardCard(left_container, title="BACKUP CONFIGURATION", icon="🛡️")
    config_card.pack(fill="x", padx=0)
    
    config_inner = InnerCard(config_card)
    
    auto_backup_row = ctk.CTkFrame(config_inner, fg_color="transparent")
    auto_backup_row.pack(fill="x", padx=20, pady=12)
    
    app.cb_auto_backup = ctk.CTkCheckBox(
        auto_backup_row, 
        text="Enable Automated Backups", 
        font=("Segoe UI", 12),
        fg_color=COLOR_NEON_BLUE,
        checkmark_color="#08080A",
        text_color="#E2E8F0",
        command=app.toggle_auto_backup
    )
    app.cb_auto_backup.pack(side="left", padx=(0, 15))
    
    ctk.CTkLabel(auto_backup_row, text="Interval:", font=("Segoe UI", 11, "bold"), text_color="#9CA3AF").pack(side="left", padx=(5, 4))
    app.ent_backup_interval = ctk.CTkEntry(
        auto_backup_row, 
        width=55, 
        justify="center", 
        fg_color="#08080A", 
        border_color="#1F2937", 
        text_color=COLOR_NEON_BLUE,
        font=("Segoe UI", 11)
    )
    app.ent_backup_interval.pack(side="left", padx=2)
    ctk.CTkLabel(auto_backup_row, text="mins", font=("Segoe UI", 11), text_color="#9CA3AF").pack(side="left", padx=(4, 15))
    
    app.btn_save_interval = ctk.CTkButton(
        auto_backup_row, 
        text="APPLY", 
        width=60, 
        height=26,
        fg_color="#16161F",
        hover_color="#1F2937",
        border_color="#1F2937",
        border_width=1,
        text_color="#E2E8F0",
        font=("Segoe UI", 11, "bold"),
        command=app.save_backup_interval
    )
    app.btn_save_interval.pack(side="left", padx=5)

    # 5. RIGHT COLUMN: HISTORICAL LOG
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    app.card_archive_container = StandardCard(right_container, title="BACKUP HISTORICAL LOG", icon="📊")
    app.card_archive_container.pack(fill="both", expand=True, padx=0)

    app.backups_scroll_container = ctk.CTkFrame(
        app.card_archive_container, 
        fg_color="#060608",
        border_color="#1F2937",
        border_width=1,
        corner_radius=6
    )
    app.backups_scroll_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))


def update_backups_list_ui(app):
    if not hasattr(app, "backups_scroll_container") or not app.backups_scroll_container:
        return

    # Update the header path label dynamically
    if hasattr(app, "lbl_backup_path_val"):
        app.lbl_backup_path_val.configure(text=f"Current Path: {str(app.backup_dir) if app.backup_dir else 'Default (Saved_Backups)'}")

    for child in app.backups_scroll_container.winfo_children():
        child.destroy()

    app.backups_scroll_container.grid_columnconfigure(0, weight=1)
    app.backups_scroll_container.grid_columnconfigure(1, weight=0)
    app.backups_scroll_container.grid_columnconfigure(2, weight=0)
    app.backups_scroll_container.grid_columnconfigure(3, weight=0)

    custom_dir = str(app.backup_dir) if app.backup_dir else None
    backups = BackupManager.get_backups_list(app.base_dir, custom_dir)

    if not backups:
        lbl_empty = ctk.CTkLabel(
            app.backups_scroll_container, 
            text="No backups found.", 
            font=("Segoe UI", 12, "italic"), 
            text_color="#9CA3AF"
        )
        lbl_empty.grid(row=0, column=0, columnspan=4, pady=30, sticky="ew")
        return

    for i, backup in enumerate(backups):
        name = backup["name"]
        path = backup["path"]
        size = backup["size"]
        date = backup["date"]

        lbl_details = ctk.CTkLabel(
            app.backups_scroll_container,
            text=f"{name}\nCreated: {date}",
            font=("Segoe UI", 11),
            text_color="#E2E8F0",
            anchor="w",
            justify="left"
        )
        lbl_details.grid(row=i, column=0, sticky="w", padx=15, pady=8)

        lbl_size = ctk.CTkLabel(
            app.backups_scroll_container,
            text=size,
            font=("JetBrains Mono", 11, "bold"),
            text_color=COLOR_NEON_BLUE
        )
        lbl_size.grid(row=i, column=1, padx=20, pady=8)

        btn_restore = ctk.CTkButton(
            app.backups_scroll_container,
            text="Restore",
            fg_color="#101014",
            hover_color="#1F2937",
            border_color=COLOR_NEON_BLUE,
            border_width=1,
            text_color=COLOR_NEON_BLUE,
            font=("Segoe UI", 11, "bold"),
            width=70,
            height=28,
            command=lambda p=path: app.trigger_backup_restore(p)
        )
        btn_restore.grid(row=i, column=2, padx=5, pady=8)

        btn_delete = ctk.CTkButton(
            app.backups_scroll_container,
            text="Delete",
            fg_color=COLOR_NEON_PINK,
            hover_color="#990033",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            width=70,
            height=28,
            command=lambda p=path: app.trigger_backup_delete(p)
        )
        btn_delete.grid(row=i, column=3, padx=(5, 15), pady=8)