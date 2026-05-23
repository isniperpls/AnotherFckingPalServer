# ==============================================================================
# views/scheduler_view.py
# Scheduler View Module - Refactored with unified Footer UI
# ==============================================================================

import customtkinter as ctk
from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

def setup_scheduler_tab(app, tab):
    """Assembles full-screen inputs and configurations using the Standard Housing chassis."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    # 1. Header
    housing.add_header(
        "Automated Restart Scheduler", 
        "Configure sequence intervals and warning alerts for automatic server restarts."
    )

    # 2. Split View Chassis
    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    
    split_chassis.grid_columnconfigure(0, weight=1, uniform="sched")
    split_chassis.grid_columnconfigure(1, weight=1, uniform="sched")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: CONFIGURATION
    # --------------------------------------------------------------------------
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Reboot Configuration
    sched_card = StandardCard(left_container, title="REBOOT CONFIGURATION", icon="⏲️")
    sched_card.pack(fill="x", padx=0)
    
    interval_inner = InnerCard(sched_card)
    duration_frame = ctk.CTkFrame(interval_inner, fg_color="transparent")
    duration_frame.pack(fill="x", padx=20, pady=12)
    
    ctk.CTkLabel(duration_frame, text="Reboot Interval:", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(side="left", padx=(0, 15))
    save_trigger = lambda e=None: app.save_manager_configs()

    app.ent_restart_hours = ctk.CTkEntry(duration_frame, width=50, justify="center", fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("Segoe UI", 12))
    app.ent_restart_hours.insert(0, "0")
    app.ent_restart_hours.bind("<KeyRelease>", save_trigger)
    app.ent_restart_hours.pack(side="left", padx=2)
    ctk.CTkLabel(duration_frame, text="hrs", font=("Segoe UI", 11), text_color="#9CA3AF").pack(side="left", padx=(2, 10))

    app.ent_restart_mins = ctk.CTkEntry(duration_frame, width=50, justify="center", fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("Segoe UI", 12))
    app.ent_restart_mins.insert(0, "30")
    app.ent_restart_mins.bind("<KeyRelease>", save_trigger)
    app.ent_restart_mins.pack(side="left", padx=2)
    ctk.CTkLabel(duration_frame, text="mins", font=("Segoe UI", 11), text_color="#9CA3AF").pack(side="left", padx=(2, 10))

    app.cb_repeat_restart = ctk.CTkCheckBox(
        sched_card, text="Enable Repeating Cycles", font=("Segoe UI", 12),
        fg_color=COLOR_NEON_BLUE, text_color="#E2E8F0", command=save_trigger
    )
    app.cb_repeat_restart.pack(anchor="w", padx=45, pady=(0, 20))

    # Broadcast Warnings
    warn_card = StandardCard(left_container, title="BROADCAST WARNINGS", icon="📢")
    warn_card.pack(fill="x", padx=0)
    warn_inner = InnerCard(warn_card)

    warnings_setup = [
        ("Warning 1:", "10", "Server restarting in 10 minutes - Please prepare!"),
        ("Warning 2:", "5", "Server restarting in 5 minutes - Prepare for logout!"),
        ("Warning 3:", "1", "Server restarting in 1 minute - Saving World!")
    ]

    for i, (label, def_min, def_msg) in enumerate(warnings_setup, 1):
        warn_row = ctk.CTkFrame(warn_inner, fg_color="transparent")
        warn_row.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(warn_row, width=65, text=label, anchor="w", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(side="left")
        
        ent_min = ctk.CTkEntry(warn_row, width=40, justify="center", fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE)
        ent_min.insert(0, def_min)
        ent_min.bind("<KeyRelease>", save_trigger)
        ent_min.pack(side="left", padx=4)
        setattr(app, f"ent_warn{i}_min", ent_min)
        
        ent_msg = ctk.CTkEntry(warn_row, fg_color="#08080A", border_color="#1F2937", text_color="#E2E8F0", placeholder_text="Warning notice...")
        ent_msg.insert(0, def_msg)
        ent_msg.bind("<KeyRelease>", save_trigger)
        ent_msg.pack(side="left", fill="x", expand=True)
        setattr(app, f"ent_warn{i}_msg", ent_msg)

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: STATUS MONITOR
    # --------------------------------------------------------------------------
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    status_card = StandardCard(right_container, title="LIVE STATUS", icon="📡")
    status_card.pack(fill="x", padx=0)
    
    status_inner = InnerCard(status_card)
    app.lbl_restart_countdown = ctk.CTkLabel(
        status_inner, text="No Active Schedule", font=("Segoe UI", 16, "bold"), text_color=COLOR_NEON_PINK
    )
    app.lbl_restart_countdown.pack(pady=30)

    # --------------------------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------------------------
    housing.footer.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
    
    ctk.CTkLabel(
        housing.footer,
        text="⚙️ Start or cancel the server reboot schedule.",
        font=("Segoe UI", 11, "italic"),
        text_color="#9CA3AF"
    ).pack(side="left", padx=20, pady=12)

    btn_frame = ctk.CTkFrame(housing.footer, fg_color="transparent")
    btn_frame.pack(side="right", padx=15, pady=10)

    app.btn_schedule_restart = ctk.CTkButton(
        btn_frame, text="START REBOOT", fg_color=COLOR_NEON_BLUE, text_color="#08080A",
        font=("Segoe UI", 12, "bold"), height=36, command=app.schedule_restart
    )
    app.btn_schedule_restart.pack(side="left", padx=(0, 8))

    app.btn_cancel_restart = ctk.CTkButton(
        btn_frame, text="CANCEL", fg_color=COLOR_NEON_PINK, text_color="#FFFFFF",
        font=("Segoe UI", 12, "bold"), height=36, command=app.cancel_restart
    )
    app.btn_cancel_restart.pack(side="left")

    try:
        app.load_stored_scheduler_settings()
    except Exception:
        pass