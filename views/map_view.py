# ==============================================================================
# views/map_view.py
# Interactive Live Map View Module - Fixed EXE Path Resolution
# ==============================================================================

import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import os
import sys
import customtkinter as ctk

from core.ui_components import StandardCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

class PalworldMapTab(ctk.CTkFrame):
    """
    Interactive Map View using a direct geometry layout for stability.
    Uses resolution-independent coordinate math ported from the JS tracker.
    Automatically centers and fits the map to the view window on launch.
    """
    def __init__(self, master, map_image_path=None):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        self.map_image_path = map_image_path
        
        # Camera/View State
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.lx = 0
        self.ly = 0
        
        # Performance & Interaction State
        self.is_interacting = False
        self._interact_timer = None
        
        self.players = []
        self.map_img = None
        self.tk_img = None
        self.map_initialized = False 

        self._setup_ui()
        self._load_map_asset()
        
        # Initial safety draw fallback
        self.after(200, self._refresh)

    def _setup_ui(self):
        """Assembles the header and canvas with absolute symmetry to other tabs."""
        # 1. Header Card
        self.header_card = StandardCard(self, title="LIVE MAP TRACKING")
        self.header_card.pack(fill="x", padx=25, pady=(20, 10))
        
        # 2. Header Description
        self.lbl_desc = ctk.CTkLabel(
            self.header_card, 
            text="Real-time coordinate mapping and topology visualization for all active server participants.",
            font=("Segoe UI", 11),
            text_color="#9CA3AF"
        )
        self.lbl_desc.pack(anchor="w", padx=25, pady=(0, 20))

        # 3. Map Canvas
        self.canvas = tk.Canvas(
            self, 
            bg="#08080A", 
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(fill="both", expand=True, padx=25, pady=(10, 25))
        
        # Interaction Bindings
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._stop_drag)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Configure>", self._on_configure)

    def _load_map_asset(self):
        """Locates the map file using EXE-safe path resolution."""
        target_path = None
        
        # Determine the root directory relative to where the app is running
        if getattr(sys, 'frozen', False):
            # If compiled as EXE, use the directory containing the EXE
            app_root = Path(sys.executable).parent.absolute()
        else:
            # If running as script, use the project root (parent of views/)
            app_root = Path(__file__).parent.parent.absolute()
        
        # Define search priorities
        candidates = [
            self.map_image_path,               # Explicit path if passed via constructor
            app_root / "map.jpg",             # Standard root JPG
            app_root / "map.png",             # Standard root PNG
            app_root / "views" / "map.jpg"    # Legacy fallback
        ]

        for cand in candidates:
            if cand and Path(cand).exists():
                target_path = Path(cand)
                break

        if target_path:
            try:
                self.map_img = Image.open(target_path)
                self.map_width, self.map_height = self.map_img.size
            except Exception:
                self._fallback_dims()
        else:
            self._fallback_dims()

    def _fallback_dims(self):
        """Failsafe dimensions if no map asset is detected."""
        self.map_width, self.map_height = 1000, 1000

    def fit_to_viewport(self):
        """Centers and fits the map inside the window."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        zoom_x = canvas_width / self.map_width
        zoom_y = canvas_height / self.map_height
        
        self.zoom = min(zoom_x, zoom_y) * 0.95
        
        self.offset_x = (canvas_width - (self.map_width * self.zoom)) / 2
        self.offset_y = (canvas_height - (self.map_height * self.zoom)) / 2
        
        self._refresh()

    def _on_configure(self, event):
        """Handles first startup auto-centering."""
        if not self.map_initialized:
            self.fit_to_viewport()
            self.map_initialized = True
        else:
            self._refresh()

    def _transform_coords(self, wx, wy):
        """Translates Unreal Engine coordinates to pixel space."""
        try:
            raw_x = float(wy) 
            raw_y = float(wx) 
        except (ValueError, TypeError):
            return 0, 0

        px_ratio = (0.0027584259 * raw_x + 0.0000024262355 * raw_y + 2036.7778) / 4000.0
        py_ratio = (-0.0000099881 * raw_x - 0.0027527692 * raw_y + 1243.0266) / 4000.0

        px = px_ratio * self.map_width
        py = py_ratio * self.map_height
        
        return px, py

    def _start_drag(self, event):
        self.is_interacting = True
        self.lx, self.ly = event.x, event.y

    def _on_drag(self, event):
        self.offset_x += event.x - self.lx
        self.offset_y += event.y - self.ly
        self.lx, self.ly = event.x, event.y
        self._refresh()

    def _stop_drag(self, event):
        self.is_interacting = False
        self._refresh()

    def _clear_interaction(self):
        self.is_interacting = False
        self._refresh()

    def _on_zoom(self, event):
        self.is_interacting = True
        if hasattr(self, "_interact_timer") and self._interact_timer:
            self.after_cancel(self._interact_timer)
            
        self._interact_timer = self.after(300, self._clear_interaction)

        factor = 1.15 if event.delta > 0 else 0.85
        new_zoom = self.zoom * factor
        
        if 0.1 < new_zoom < 10.0:
            mouse_x, mouse_y = event.x, event.y
            unscaled_x = (mouse_x - self.offset_x) / self.zoom
            unscaled_y = (mouse_y - self.offset_y) / self.zoom
            self.zoom = new_zoom
            self.offset_x = mouse_x - (unscaled_x * self.zoom)
            self.offset_y = mouse_y - (unscaled_y * self.zoom)
            self._refresh()

    def update_player_positions(self, player_data):
        self.players = player_data
        self._refresh()

    def _refresh(self):
        """Repaints the map and overlays with optimized viewport-based cropping."""
        self.canvas.delete("all")
        
        if self.map_img:
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            
            if canvas_w <= 1: canvas_w = 800
            if canvas_h <= 1: canvas_h = 600

            img_w = self.map_width * self.zoom
            img_h = self.map_height * self.zoom

            left_bound = max(0.0, -self.offset_x)
            right_bound = min(img_w, canvas_w - self.offset_x)
            top_bound = max(0.0, -self.offset_y)
            bottom_bound = min(img_h, canvas_h - self.offset_y)

            crop_left = left_bound / self.zoom
            crop_right = right_bound / self.zoom
            crop_top = top_bound / self.zoom
            crop_bottom = bottom_bound / self.zoom

            crop_left = max(0.0, min(self.map_width, crop_left))
            crop_right = max(0.0, min(self.map_width, crop_right))
            crop_top = max(0.0, min(self.map_height, crop_top))
            crop_bottom = max(0.0, min(self.map_height, crop_bottom))

            if crop_right > crop_left and crop_bottom > crop_top:
                cropped_img = self.map_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                resize_w = int((crop_right - crop_left) * self.zoom)
                resize_h = int((crop_bottom - crop_top) * self.zoom)

                if resize_w > 0 and resize_h > 0:
                    filter_mode = Image.Resampling.NEAREST if self.is_interacting else Image.Resampling.BILINEAR
                    img_resized = cropped_img.resize((resize_w, resize_h), filter_mode)
                    self.tk_img = ImageTk.PhotoImage(img_resized)
                    draw_x = max(0.0, self.offset_x)
                    draw_y = max(0.0, self.offset_y)
                    self.canvas.create_image(draw_x, draw_y, image=self.tk_img, anchor="nw")
        else:
            self.canvas.create_text(
                self.winfo_width()//2, 300, 
                text="MAP ASSET NOT FOUND\nPlace 'map.jpg' or 'map.png' in the root directory.", 
                fill=COLOR_NEON_PINK, font=("Segoe UI", 12, "bold"), justify="center"
            )

        for p in self.players:
            px, py = self._transform_coords(p.get('location_x', 0), p.get('location_y', 0))
            x, y = (px * self.zoom) + self.offset_x, (py * self.zoom) + self.offset_y
            
            # Marker Core
            self.canvas.create_oval(x-7, y-7, x+7, y+7, fill="#2ecc71", outline="white", width=2)
            # Player Name
            self.canvas.create_text(
                x, y-18, text=p.get('name', 'Player'), 
                fill="white", font=("Segoe UI", 9, "bold")
            )