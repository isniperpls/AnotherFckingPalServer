# ==============================================================================
# views/metrics_view.py
# Detailed Server Metrics Tab View Module
# Refactored to match standard split-grid designs, headers, and color telemetry.
# ==============================================================================

import customtkinter as ctk
import time
from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

def setup_metrics_tab(app, tab):
    """Assembles the detailed server metrics view using standard layout patterns."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)
    
    # Store container references
    app.metrics_scroll_container = housing.container

    # 1. Header Card
    housing.add_header(
        "Detailed Server Metrics",
        "Monitor game engine frame performance, tick frequencies, in-game clock states, and live limits."
    )

    # 2. Split View Chassis
    split_chassis = ctk.CTkFrame(app.metrics_scroll_container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    
    split_chassis.grid_columnconfigure(0, weight=4, uniform="metrics_split")
    split_chassis.grid_columnconfigure(1, weight=6, uniform="metrics_split")
    split_chassis.grid_rowconfigure(0, weight=1)

    # Left Container: Engine Performance Gauges and World Stats
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Right Container: Engine Activity Metrics & Logs
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # --- LEFT PANEL: GAME ENGINE TELEMETRY ---
    telemetry_card = StandardCard(left_container, title="ENGINE PERFORMANCE GAUGES", icon="⚡")
    telemetry_card.pack(fill="x", padx=0)

    # Server FPS Gauge
    fps_tile = ctk.CTkFrame(telemetry_card, fg_color="#12121A", border_color="#1F2937", border_width=1, corner_radius=6)
    fps_tile.pack(fill="x", padx=20, pady=6)
    app.lbl_server_fps_val = ctk.CTkLabel(fps_tile, text="Server FPS: Offline", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0")
    app.lbl_server_fps_val.pack(anchor="w", padx=15, pady=(10, 5))
    app.bar_server_fps = ctk.CTkProgressBar(fps_tile, height=6, progress_color=COLOR_NEON_BLUE, fg_color="#1F1F2A")
    app.bar_server_fps.set(0.0)
    app.bar_server_fps.pack(fill="x", padx=15, pady=(0, 12))

    # Frame Time Gauge
    frame_tile = ctk.CTkFrame(telemetry_card, fg_color="#12121A", border_color="#1F2937", border_width=1, corner_radius=6)
    frame_tile.pack(fill="x", padx=20, pady=6)
    app.lbl_frame_time_val = ctk.CTkLabel(frame_tile, text="Server Frame Time: N/A", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0")
    app.lbl_frame_time_val.pack(anchor="w", padx=15, pady=(10, 5))
    app.bar_frame_time = ctk.CTkProgressBar(frame_tile, height=6, progress_color=COLOR_NEON_BLUE, fg_color="#1F1F2A")
    app.bar_frame_time.set(0.0)
    app.bar_frame_time.pack(fill="x", padx=15, pady=(0, 12))

    # --- LEFT PANEL: WORLD & PLAYER TELEMETRY ---
    world_card = StandardCard(left_container, title="WORLD TELEMETRY STATS", icon="🌍")
    world_card.pack(fill="x", padx=0)
    
    world_inner = InnerCard(world_card)
    world_inner.pack(fill="x", padx=15, pady=(0, 15))

    # Active Players Count
    app.lbl_metrics_players = ctk.CTkLabel(world_inner, text="Active Players: N/A", font=("Segoe UI", 12, "bold"), text_color="#E2E8F0")
    app.lbl_metrics_players.pack(anchor="w", padx=20, pady=(15, 6))

    # In-Game Days Count
    app.lbl_ingame_days = ctk.CTkLabel(world_inner, text="In-Game Time: N/A", font=("Segoe UI", 12, "bold"), text_color="#E2E8F0")
    app.lbl_ingame_days.pack(anchor="w", padx=20, pady=6)

    # Active Base Camps Count
    app.lbl_basecamp_count = ctk.CTkLabel(world_inner, text="Active Base Camps: N/A", font=("Segoe UI", 12, "bold"), text_color="#E2E8F0")
    app.lbl_basecamp_count.pack(anchor="w", padx=20, pady=6)

    # Server Uptime State
    app.lbl_uptime_count = ctk.CTkLabel(world_inner, text="Server Uptime: Offline", font=("Segoe UI", 12, "bold"), text_color=COLOR_NEON_PINK)
    app.lbl_uptime_count.pack(anchor="w", padx=20, pady=(6, 15))

    # --- RIGHT PANEL: PERFORMANCE RECORD LOGGER ---
    log_card = StandardCard(right_container, title="METRICS HISTORICAL TRACKER", icon="📈")
    log_card.pack(fill="both", expand=True, padx=0)

    app.metrics_log_view = ctk.CTkTextbox(
        log_card, 
        font=("JetBrains Mono", 10), 
        fg_color="#060608", 
        border_color="#1F2937", 
        border_width=1, 
        text_color="#E2E8F0"
    )
    app.metrics_log_view.pack(fill="both", expand=True, padx=25, pady=(0, 25))

def format_uptime(total_seconds):
    """Formats raw uptime seconds cleanly as DD:HH:MM:SS."""
    try:
        seconds = int(total_seconds)
    except (ValueError, TypeError):
        return "Offline"
        
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if days > 0:
        return f"{days}d {hours:02d}h {minutes:02d}m {secs:02d}s"
    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"

def update_metrics_ui(app, data):
    """Updates metrics text elements, historical performance charts, and logical widgets."""
    if not hasattr(app, "lbl_server_fps_val") or not app.lbl_server_fps_val:
        return

    # Extract all REST payload keys
    fps = data.get("serverfps", 0)
    current_players = data.get("currentplayernum", 0)
    frame_time = data.get("serverframetime", 0.0)
    max_players = data.get("maxplayernum", 0)
    uptime = data.get("uptime", 0)
    basecamps = data.get("basecampnum", "N/A")
    days = data.get("days", 0)

    # 1. Update text variables
    app.lbl_server_fps_val.configure(text=f"Server Frame Pass (FPS): {fps} FPS")
    app.lbl_frame_time_val.configure(text=f"Server Tick Calculation Time: {frame_time:.2f} ms")
    
    if hasattr(app, "lbl_metrics_players"):
        app.lbl_metrics_players.configure(text=f"Active Players: {current_players} / {max_players}")
        
    app.lbl_ingame_days.configure(text=f"World Calendar: Day {days}")
    app.lbl_basecamp_count.configure(text=f"Active World Base Camps: {basecamps}")
    app.lbl_uptime_count.configure(text=f"Server Active Uptime: {format_uptime(uptime)}", text_color=COLOR_NEON_BLUE)

    # 2. Update status bar progress scaling
    # Standard server target is 60 FPS
    fps_pct = min(1.0, max(0.0, fps / 60.0))
    app.bar_server_fps.set(fps_pct)

    # target is usually below 16.6ms (equivalent to stable 60Hz loop)
    ft_pct = min(1.0, max(0.0, frame_time / 33.3))
    app.bar_frame_time.set(ft_pct)

    # 3. Append to history logger
    if hasattr(app, "metrics_log_view"):
        timestamp = time.strftime('%H:%M:%S')
        log_str = (
            f"[{timestamp}] Frame Rate: {fps} FPS | Tick: {frame_time:.2f} ms | "
            f"Players: {current_players}/{max_players} | Bases: {basecamps} | Days: {days}\n"
        )
        
        # Ensure log buffer doesn't overflow
        current_content = app.metrics_log_view.get("1.0", "end")
        if len(current_content.splitlines()) > 100:
            app.metrics_log_view.delete("1.0", "2.0")
            
        app.metrics_log_view.insert("end", log_str)
        app.metrics_log_view.see("end")

def set_metrics_offline_ui(app, error_msg):
    """Sets metrics UI elements to offline fallback state on API drop."""
    if not hasattr(app, "lbl_server_fps_val") or not app.lbl_server_fps_val:
        return

    app.lbl_server_fps_val.configure(text=f"Server FPS: Offline ({error_msg})")
    app.bar_server_fps.set(0.0)
    app.lbl_frame_time_val.configure(text="Server Frame Time: N/A")
    app.bar_frame_time.set(0.0)
    
    if hasattr(app, "lbl_metrics_players"):
        app.lbl_metrics_players.configure(text="Active Players: Offline")
        
    app.lbl_ingame_days.configure(text="World Calendar: N/A")
    app.lbl_basecamp_count.configure(text="Active World Base Camps: N/A")
    app.lbl_uptime_count.configure(text="Server Uptime: Offline", text_color=COLOR_NEON_PINK)