# ==============================================================================
# Tooltip Component Module
# Contains the hoverable ToolTip class bound to TK widgets.
# ==============================================================================

import tkinter as tk

class ToolTip:
    """Lightweight tooltip widget for displaying parameter descriptions on hover."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        # Position slightly offset from the mouse cursor
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-disabled", True) # Ignore pointer inputs to allow seamless mouse movement
        
        label = tk.Label(
            tw, 
            text=self.text, 
            justify="left", 
            background="#2d2d30", 
            foreground="#f0f0f0",
            relief="solid", 
            borderwidth=1,
            font=("Segoe UI", 10),
            padx=10,
            pady=6,
            wraplength=350 # Prevents long single-line stretching
        )
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()