# ==============================================================================
# views/dashboard_view.py
# Dashboard View Module
# ==============================================================================

import customtkinter as ctk
from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

def setup_dashboard_tab(app, tab):
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    housing.add_header("Dashboard Overview", "Real-time system telemetry and core server infrastructure status.")

    # Wrapper frame to handle the split columns so we don't mix grid/pack on the housing container
    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    
    split_chassis.grid_columnconfigure(0, weight=4, uniform="dash")
    split_chassis.grid_columnconfigure(1, weight=6, uniform="dash")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: SYSTEM VITALS
    # --------------------------------------------------------------------------
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    status_card = StandardCard(left_container, title="INFRASTRUCTURE STATUS", icon="📡")
    status_card.pack(fill="x", padx=0) 
    
    status_inner = InnerCard(status_card)
    status_inner.pack(fill="x", padx=15, pady=(0, 15))
    
    status_row = ctk.CTkFrame(status_inner, fg_color="transparent")
    status_row.pack(fill="x", padx=20, pady=(12, 6))
    ctk.CTkLabel(status_row, text="Server Status:", font=("Segoe UI", 12, "bold"), text_color="#9CA3AF").pack(side="left")
    app.lbl_quick_status_val = ctk.CTkLabel(status_row, text="OFFLINE", font=("Segoe UI", 12, "bold"), text_color=COLOR_NEON_PINK)
    app.lbl_quick_status_val.pack(side="left", padx=6)

    args_row = ctk.CTkFrame(status_inner, fg_color="transparent")
    args_row.pack(fill="x", padx=20, pady=6)
    ctk.CTkLabel(args_row, text="CLI Flags:", font=("Segoe UI", 11, "bold"), text_color="#9CA3AF").pack(side="left")
    app.ent_launch_args = ctk.CTkEntry(args_row, fg_color="#08080A", border_color="#1F2937", text_color="#E2E8F0", font=("Segoe UI", 11), height=26)
    app.ent_launch_args.pack(side="left", fill="x", expand=True, padx=(6, 0))

    app.lbl_player_count = ctk.CTkLabel(status_inner, text="Players: 0/32", font=("Segoe UI", 11, "bold"), text_color=COLOR_NEON_BLUE)
    app.lbl_player_count.pack(anchor="w", padx=20, pady=(10, 0))

    app.lbl_dashboard_restart_countdown = ctk.CTkLabel(status_inner, text="Next Restart in: Disabled", font=("Segoe UI", 11), text_color="#9CA3AF")
    app.lbl_dashboard_restart_countdown.pack(anchor="w", padx=20, pady=(0, 12))
    
    app.bar_restart_progress = ctk.CTkProgressBar(status_card, height=2, progress_color=COLOR_NEON_BLUE, fg_color="#1F2937")
    app.bar_restart_progress.set(0.0)
    app.bar_restart_progress.pack(fill="x", padx=25, pady=(0, 20))

    hw_card = StandardCard(left_container, title="SYSTEM TELEMETRY", icon="📊")
    hw_card.pack(fill="x", padx=0)
    
    def create_v_meter(parent, label_var_name, bar_var_name):
        tile = ctk.CTkFrame(parent, fg_color="#12121A", border_color="#1F2937", border_width=1, corner_radius=6)
        tile.pack(fill="x", padx=20, pady=6)
        lbl = ctk.CTkLabel(tile, text="Loading...", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0")
        lbl.pack(anchor="w", padx=15, pady=(10, 5))
        bar = ctk.CTkProgressBar(tile, height=6, progress_color=COLOR_NEON_BLUE, fg_color="#1F1F2A")
        bar.set(0.0)
        bar.pack(fill="x", padx=15, pady=(0, 12))
        setattr(app, label_var_name, lbl)
        setattr(app, bar_var_name, bar)

    create_v_meter(hw_card, "lbl_cpu_val", "bar_cpu")
    create_v_meter(hw_card, "lbl_ram_val", "bar_ram")
    create_v_meter(hw_card, "lbl_disk_val", "bar_disk")

    # Re-added the missing Network Throughput Tile
    net_tile = ctk.CTkFrame(hw_card, fg_color="#12121A", border_color="#1F2937", border_width=1, corner_radius=6)
    net_tile.pack(fill="x", padx=20, pady=(6, 20))
    app.lbl_net_val = ctk.CTkLabel(net_tile, text="Network: Up: 0 KB/s | Down: 0 KB/s", font=("Segoe UI", 10, "bold"), text_color="#E2E8F0")
    app.lbl_net_val.pack(anchor="w", padx=15, pady=(10, 2))
    app.lbl_net_totals = ctk.CTkLabel(net_tile, text="Total: 0 GB Sent | 0 GB Recv", font=("Segoe UI", 9, "italic"), text_color="#9CA3AF")
    app.lbl_net_totals.pack(anchor="w", padx=15, pady=(0, 10))

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: LOGS & DEPLOYMENT
    # --------------------------------------------------------------------------
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    install_card = StandardCard(right_container, title="SERVER DEPLOYMENT", icon="🚀")
    install_card.pack(fill="x", padx=0)
    
    install_inner = InnerCard(install_card)
    install_inner.pack(fill="x", padx=15, pady=(0, 15))
    
    install_layout = ctk.CTkFrame(install_inner, fg_color="transparent")
    install_layout.pack(fill="x", padx=20, pady=12)
    ctk.CTkLabel(install_layout, text="SteamCMD Service:", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(side="left")
    app.btn_install_server = ctk.CTkButton(install_layout, text="INSTALL / UPDATE", width=140, height=28, fg_color="#16161F", border_color=COLOR_NEON_BLUE, border_width=1, text_color=COLOR_NEON_BLUE, font=("Segoe UI", 11, "bold"))
    app.btn_install_server.pack(side="right")

    log_card = StandardCard(right_container, title="CORE SYSTEM LOGS", icon="💻")
    log_card.pack(fill="both", expand=True, padx=0)
    
    app.log_view = ctk.CTkTextbox(log_card, font=("JetBrains Mono", 10), fg_color="#060608", border_color="#1F2937", border_width=1, text_color="#E2E8F0", height=404)
    app.log_view.pack(fill="both", expand=True, padx=25, pady=(0, 19))

    app.player_list_view = ctk.CTkTextbox(tab, height=0, width=0)
    app.lbl_palserver_ram = ctk.CTkLabel(tab, text="")