# ==============================================================================
# core/ui_components.py
# Centralized UI Chassis & Component Module
# ==============================================================================

import customtkinter as ctk

# --- GLOBAL DESIGN CONSTANTS ---
PAD_OUTER = 15      
PAD_INTERNAL = 25   
PAD_Y = 20          
COLOR_DARK_BG = "#0D0D11"
COLOR_CARD_BG = "#0D0D11"    # Obsidian Black card background
COLOR_FIELD_BG = "#101014"   
COLOR_NEON_BLUE = "#00E5FF"  
COLOR_NEON_PINK = "#FF3366"  
COLOR_TEXT_DIM = "#9CA3AF"   

class StandardTab(ctk.CTkFrame):
    """Base housing with obsidian header card and color-matched scrollbars."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 

        self.scroll_canvas = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#0D0D11",
            scrollbar_button_hover_color="#0D0D11",
            scrollbar_fg_color="transparent"
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew", padx=PAD_OUTER, pady=(PAD_OUTER, 5))
        self.scroll_canvas.grid_columnconfigure(0, weight=1)
        
        self.container = self.scroll_canvas
        self.footer = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, border_color="#1F2937", border_width=1, corner_radius=8)

    def add_header(self, title, description):
        """Wraps the header in its own Obsidian Black card for consistency."""
        header_card = StandardCard(self.container)
        header_card.pack(fill="x", padx=PAD_INTERNAL, pady=(0, 15))
        
        lbl_title = ctk.CTkLabel(header_card, text=title, font=("Segoe UI", 16, "bold"), text_color=COLOR_NEON_BLUE)
        lbl_title.pack(anchor="w", padx=25, pady=(20, 2))
        
        lbl_desc = ctk.CTkLabel(header_card, text=description, font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM)
        lbl_desc.pack(anchor="w", padx=25, pady=(0, 20))
        return header_card

class StandardCard(ctk.CTkFrame):
    """The signature #0D0D11 Dark Card with standardized borders and padding."""
    def __init__(self, master, title=None, icon=None, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD_BG, border_color="#1F2937", border_width=1, corner_radius=8, **kwargs)
        self.pack(fill="x", padx=PAD_INTERNAL, pady=(0, 15))
        if title:
            display_text = f"{icon} {title}" if icon else title
            self.lbl_title = ctk.CTkLabel(self, text=display_text, font=("Segoe UI", 13, "bold"), text_color=COLOR_NEON_BLUE)
            self.lbl_title.pack(anchor="w", padx=PAD_INTERNAL, pady=(PAD_Y, 10))

class InnerCard(ctk.CTkFrame):
    """Nested #101014 frame for grouping inputs inside a Dark Card."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_FIELD_BG, border_color="#1F2937", border_width=1, corner_radius=8, **kwargs)
        self.pack(fill="x", padx=PAD_INTERNAL, pady=(0, PAD_Y))