# ==============================================================================
# views/converter_view.py
# Co-Op / Single-Player to Dedicated Server Save Converter View
# Refactored to use the Standard UI Housing and Split-View Layout.
# ==============================================================================

import os
import zlib
import time
import uuid 
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE

def setup_converter_tab(app, tab):
    """Assembles the UI using the Standard Housing chassis with split view."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    # 1. Header Card
    housing.add_header(
        "Save Data Migration Converter", 
        "Migrate single-player or local co-op save files over to a dedicated server environment safely."
    )

    # 2. Split View Chassis
    split_chassis = ctk.CTkFrame(housing.container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)
    
    split_chassis.grid_columnconfigure(0, weight=1, uniform="conv")
    split_chassis.grid_columnconfigure(1, weight=1, uniform="conv")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: MIGRATION MAPPING
    # --------------------------------------------------------------------------
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    mapping_card = StandardCard(left_container, title="MIGRATION MAPPING", icon="🆔")
    mapping_card.pack(fill="x", padx=0)
    
    files_inner = InnerCard(mapping_card)
    
    # Source Level.sav Row
    level_row = ctk.CTkFrame(files_inner, fg_color="transparent")
    level_row.pack(fill="x", padx=20, pady=12)
    ctk.CTkLabel(level_row, text="Source Level.sav:", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(side="left")
    
    btn_browse_level = ctk.CTkButton(
        level_row, text="BROWSE", width=100, height=28, fg_color="#16161F", hover_color="#1F2937",
        border_color="#1F2937", border_width=1, text_color="#E2E8F0", font=("Segoe UI", 11, "bold"),
        command=lambda: browse_level_sav(app)
    )
    btn_browse_level.pack(side="right")
    
    app.ent_conv_level_path = ctk.CTkEntry(level_row, width=220, fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("JetBrains Mono", 11), placeholder_text="Path to Level.sav...")
    app.ent_conv_level_path.pack(side="right", padx=10)

    # Output Row
    output_row = ctk.CTkFrame(files_inner, fg_color="transparent")
    output_row.pack(fill="x", padx=20, pady=(0, 12))
    ctk.CTkLabel(output_row, text="Output Directory:", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(side="left")
    
    btn_browse_output = ctk.CTkButton(
        output_row, text="CHOOSE", width=100, height=28, fg_color="#16161F", hover_color="#1F2937",
        border_color="#1F2937", border_width=1, text_color="#E2E8F0", font=("Segoe UI", 11, "bold"),
        command=lambda: browse_output_directory(app)
    )
    btn_browse_output.pack(side="right")
    
    app.ent_conv_output_path = ctk.CTkEntry(output_row, width=220, fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("JetBrains Mono", 11), placeholder_text="Target folder...")
    app.ent_conv_output_path.pack(side="right", padx=10)

    # SteamID Inner Card
    id_inner = InnerCard(mapping_card)
    id_row = ctk.CTkFrame(id_inner, fg_color="transparent")
    id_row.pack(fill="x", padx=20, pady=12)
    ctk.CTkLabel(id_row, text="Target ID:", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0").pack(anchor="w", pady=(0,5))
    
    app.ent_conv_player_id = ctk.CTkEntry(id_row, width=440, fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("JetBrains Mono", 11), placeholder_text="7656119... or GUID")
    app.ent_conv_player_id.pack(fill="x")

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: LOGS
    # --------------------------------------------------------------------------
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    logs_card = StandardCard(right_container, title="EXECUTION OUTPUT LOGS", icon="💻")
    logs_card.pack(fill="both", expand=True, padx=0)
    
    app.conv_log_view = ctk.CTkTextbox(
        logs_card, font=("JetBrains Mono", 10), fg_color="#060608", 
        border_color="#1F2937", border_width=1, text_color="#E2E8F0", height=300
    )
    app.conv_log_view.pack(fill="both", expand=True, padx=25, pady=(0, 25))

    # --------------------------------------------------------------------------
    # FIXED FOOTER
    # --------------------------------------------------------------------------
    housing.footer.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
    
    ctk.CTkLabel(
        housing.footer,
        text="⚠️ Conversion logic overwrites host GUIDs. Ensure a backup is made first.",
        font=("Segoe UI", 11, "italic"),
        text_color="#9CA3AF"
    ).pack(side="left", padx=20, pady=12)

    app.btn_execute_conversion = ctk.CTkButton(
        housing.footer,
        text="EXECUTE WORLD DATA CONVERSION",
        height=36,
        width=260,
        fg_color=COLOR_NEON_BLUE,
        hover_color="#00B4CC",
        text_color="#08080A",
        font=("Segoe UI", 12, "bold"),
        command=lambda: start_conversion_pipeline(app)
    )
    app.btn_execute_conversion.pack(side="right", padx=15, pady=10)

# --- Logic Functions ---
def browse_level_sav(app):
    selected = filedialog.askopenfilename(title="Select Level.sav", filetypes=[("Save file", "Level.sav"), ("All saves", "*.sav")])
    if selected:
        app.ent_conv_level_path.delete(0, "end")
        app.ent_conv_level_path.insert(0, selected)
        append_conv_log(app, f"Selected Level.sav: {selected}")

def browse_output_directory(app):
    selected = filedialog.askdirectory(title="Select Output Folder")
    if selected:
        app.ent_conv_output_path.delete(0, "end")
        app.ent_conv_output_path.insert(0, selected)
        append_conv_log(app, f"Output directory set: {selected}")

def append_conv_log(app, msg):
    if hasattr(app, "conv_log_view"):
        app.conv_log_view.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        app.conv_log_view.see("end")

def start_conversion_pipeline(app):
    level_path_str = app.ent_conv_level_path.get().strip()
    output_path_str = app.ent_conv_output_path.get().strip()
    new_id_str = app.ent_conv_player_id.get().strip()

    if not level_path_str or not os.path.exists(level_path_str):
        messagebox.showwarning("Warning", "Select a valid source Level.sav first.")
        return
    if not output_path_str or not os.path.exists(output_path_str):
        messagebox.showwarning("Warning", "Select a valid destination directory.")
        return
    if not new_id_str:
        messagebox.showwarning("Warning", "Target network ID cannot be blank.")
        return

    app.btn_execute_conversion.configure(state="disabled", text="PROCESSING...")
    threading.Thread(target=run_conversion_worker, args=(app, Path(level_path_str), Path(output_path_str), new_id_str), daemon=True).start()

def run_conversion_worker(app, level_path, output_root, new_id_str):
    try:
        app.after(0, lambda: append_conv_log(app, "Initializing conversion..."))
        clean_input = new_id_str.replace("-", "").strip().lower()
        target_sav_filename = "00000000000000000000000000000001.sav"
        
        if clean_input.isdigit():
            steam_id_int = int(clean_input)
            steam_bytes = steam_id_int.to_bytes(8, byteorder='little')
            new_guid_bytes = steam_bytes + b"\x00\x00\x00\x00\x00\x00\x00\x00"
            raw_guid = uuid.UUID(bytes=new_guid_bytes)
            target_sav_filename = f"{str(raw_guid).upper().replace('-', '')}.sav"
        else:
            if len(clean_input) < 32: clean_input = clean_input.ljust(32, "0")
            try:
                new_guid_bytes = bytes.fromhex(clean_input[:32])
                raw_guid = uuid.UUID(hex=clean_input[:32])
                target_sav_filename = f"{str(raw_guid).upper().replace('-', '')}.sav"
            except ValueError:
                raise Exception("Invalid ID format.")

        old_guid_bytes = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"
        target_export_dir = output_root / f"Converted_Save_{int(time.time())}"
        target_export_players_dir = target_export_dir / "Players"
        target_export_players_dir.mkdir(parents=True, exist_ok=True)

        raw_bytes = level_path.read_bytes()
        decompressed_data = None
        for offset in range(0, min(64, len(raw_bytes))):
            try:
                decompressed_data = zlib.decompress(raw_bytes[offset:], zlib.MAX_WBITS | 32)
                break
            except Exception:
                try:
                    decompressed_data = zlib.decompress(raw_bytes[offset:], -zlib.MAX_WBITS)
                    break
                except Exception: continue

        if decompressed_data is None: raise Exception("Decompression failed.")
        modified_data = decompressed_data.replace(old_guid_bytes, new_guid_bytes)

        compressor = zlib.compressobj(zlib.Z_BEST_SPEED, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        new_compressed_body = compressor.compress(modified_data) + compressor.flush()
        
        final_file_bytes = len(modified_data).to_bytes(4, byteorder='little') + len(new_compressed_body).to_bytes(4, byteorder='little') + b"PLWS" + new_compressed_body
        (target_export_dir / "Level.sav").write_bytes(final_file_bytes)

        source_host_player_file = level_path.with_name("Players") / "00000000000000000000000000000001.sav"
        if source_host_player_file.exists():
            player_bytes = source_host_player_file.read_bytes()
            p_decompressed = None
            for p_offset in range(0, min(64, len(player_bytes))):
                try:
                    p_decompressed = zlib.decompress(player_bytes[p_offset:], zlib.MAX_WBITS | 32)
                    break
                except Exception: continue

            if p_decompressed is not None:
                p_modified = p_decompressed.replace(old_guid_bytes, new_guid_bytes)
                p_compressor = zlib.compressobj(zlib.Z_BEST_SPEED, zlib.DEFLATED, zlib.MAX_WBITS | 16)
                p_compressed_body = p_compressor.compress(p_modified) + p_compressor.flush()
                p_final_bytes = len(p_modified).to_bytes(4, byteorder='little') + len(p_compressed_body).to_bytes(4, byteorder='little') + b"PLWS" + p_compressed_body
                (target_export_players_dir / target_sav_filename).write_bytes(p_final_bytes)

        app.after(0, lambda: append_conv_log(app, "✅ Conversion finished smoothly!"))
        app.after(0, lambda: messagebox.showinfo("Success", f"Files generated here:\n{target_export_dir}"))

    except Exception as err:
        app.after(0, lambda: append_conv_log(app, f"❌ [Fatal Error]: {err}"))
        app.after(0, lambda: messagebox.showerror("Failure", str(err)))
    finally:
        app.after(0, lambda: app.btn_execute_conversion.configure(state="normal", text="EXECUTE WORLD DATA CONVERSION"))