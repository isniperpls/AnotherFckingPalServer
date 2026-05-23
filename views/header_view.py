# ==============================================================================
# views/header_view.py
# Header View Module
# Constructs the persistent navigation, global server control bar, and support.
# ==============================================================================

import webbrowser
import customtkinter as ctk
from core.ui_components import COLOR_FIELD_BG, COLOR_NEON_BLUE, COLOR_NEON_PINK, COLOR_DARK_BG

def setup_header_bar(app):
    """Constructs horizontal header navigation bar, main server controls, and support button."""
    # Top Header Bar Chassis (Matching standard Obsidian Black & Neon Blue theme)
    app.header = ctk.CTkFrame(
        app, 
        height=85, # Fixed height for stable visual weight
        corner_radius=0, 
        fg_color=COLOR_FIELD_BG, 
        border_color="#1F2937", 
        border_width=1
    )
    app.header.pack(side="top", fill="x")
    app.header.pack_propagate(False)
    
    # --- LOGO SECTION ---
    # We omit fill="y" to let Tkinter's pack manager handle perfect vertical centering
    app.logo_frame = ctk.CTkFrame(app.header, fg_color="transparent")
    app.logo_frame.pack(side="left", padx=25)
    
    app.lbl_logo = ctk.CTkLabel(
        app.logo_frame, 
        text="ANOTHER FCKING", 
        font=("Urbanist", 22, "bold"), 
        text_color=COLOR_NEON_BLUE
    )
    app.lbl_logo.pack(side="left")
    
    app.lbl_logo_sub = ctk.CTkLabel(
        app.logo_frame, 
        text=" SERVER MANAGER", 
        font=("Urbanist", 16, "bold"), 
        text_color="#E2E8F0"
    )
    app.lbl_logo_sub.pack(side="left", padx=(4, 0))

    # --- GLOBAL CONTROL BUTTONS ---
    # We omit fill="y" here as well to cleanly align buttons center-mass
    app.header_btn_frame = ctk.CTkFrame(app.header, fg_color="transparent")
    app.header_btn_frame.pack(side="right", padx=25)
    
    # Premium Outlined Support Button (Neon Pink Accent)
    # Open-source friendly, completely optional, and matches application styling.
    app.btn_support = ctk.CTkButton(
        app.header_btn_frame, 
        text="💖 SUPPORT", 
        fg_color="transparent", 
        hover_color="#2A161A", # Dark burgundy/pink hover state
        border_color=COLOR_NEON_PINK, 
        border_width=1, 
        text_color=COLOR_NEON_PINK, 
        font=("Segoe UI", 12, "bold"),
        height=38,
        width=110,
        # Replace the URL below with your Ko-fi, GitHub Sponsors, or PayPal link!
        command=lambda: webbrowser.open_new_tab("https://ko-fi.com/Ecks")
    )
    app.btn_support.pack(side="left", padx=10)
    
    # Path Browser Button
    app.btn_browse = ctk.CTkButton(
        app.header_btn_frame, 
        text="SET SERVER PATH", 
        fg_color="#16161F", 
        hover_color="#1F1F2A", 
        border_color=COLOR_NEON_BLUE, 
        border_width=1, 
        text_color=COLOR_NEON_BLUE, 
        font=("Segoe UI", 12, "bold"),
        height=38,
        command=app.browse_path
    )
    app.btn_browse.pack(side="left", padx=10)
    
    # Main Server Toggle (Start/Stop)
    app.btn_toggle = ctk.CTkButton(
        app.header_btn_frame, 
        text="START SERVER", 
        fg_color=COLOR_NEON_BLUE, 
        hover_color="#00B4CC", 
        text_color="#08080A", 
        font=("Segoe UI", 12, "bold"),
        height=38,
        command=app.toggle_server
    )
    app.btn_toggle.pack(side="left", padx=10)