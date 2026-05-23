# ==============================================================================
# views/mods_view.py
# Mods & Plugins Manager View Module
# Handles UE4SS framework automation, Mod deployment, and active directory toggles.
# ==============================================================================

import os
import json
import shutil
import urllib.request
import zipfile
import threading
import time
from pathlib import Path
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog

from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE, COLOR_NEON_PINK

# Stable offline fallback URL in case GitHub API blocks or fails
FALLBACK_UE4SS_URL = "https://github.com/UE4SS-RE/RE-UE4SS/releases/download/v3.0.1/UE4SS_v3.0.1.zip"

def get_latest_ue4ss_download_url():
    """
    Queries the GitHub API to dynamically resolve the latest release zip of RE-UE4SS.
    Returns a tuple of (download_url, tag_name).
    """
    api_url = "https://api.github.com/repos/UE4SS-RE/RE-UE4SS/releases/latest"
    try:
        # Construct request with user-agent header to avoid GitHub API connection blockages
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'PalworldServerManager-Client/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            assets = data.get("assets", [])
            tag_name = data.get("tag_name", "Latest")

            # 1. Look for matching standard non-experimental release zip asset
            for asset in assets:
                name = asset.get("name", "")
                if name.startswith("UE4SS_") and name.endswith(".zip") and not "experimental" in name.lower():
                    download_url = asset.get("browser_download_url")
                    if download_url:
                        return download_url, tag_name

            # 2. Fallback check for any zip naming variant containing 'ue4ss'
            for asset in assets:
                name = asset.get("name", "")
                if "ue4ss" in name.lower() and name.endswith(".zip"):
                    download_url = asset.get("browser_download_url")
                    if download_url:
                        return download_url, tag_name

            return FALLBACK_UE4SS_URL, tag_name
    except Exception:
        # Fall back to safe offline hardcoded version silently on rate limits or offline scenarios
        return FALLBACK_UE4SS_URL, "v3.0.1"

def setup_mods_tab(app, tab):
    """Sets up the split layout grid and dashboard controls for Server Mods and Plugins."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)

    # Store container references
    app.mods_scroll_container = housing.container
    app.selected_mods_vars = {}  # Tracks file/dir paths to CTK BooleanVars for selection state

    # 1. Header Card
    housing.add_header(
        "Mods & Plugins Manager",
        "Install the UE4SS scripting framework, deploy game modifications, and toggle active mod packages."
    )

    # 2. Split View Chassis
    split_chassis = ctk.CTkFrame(app.mods_scroll_container, fg_color="transparent")
    split_chassis.pack(fill="both", expand=True, padx=25)

    split_chassis.grid_columnconfigure(0, weight=4, uniform="mods_split")
    split_chassis.grid_columnconfigure(1, weight=6, uniform="mods_split")
    split_chassis.grid_rowconfigure(0, weight=1)

    # Left Column: Framework & Deployment
    left_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Right Column: Active Registry List
    right_container = ctk.CTkFrame(split_chassis, fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # --- LEFT CONTAINER: UE4SS FRAMEWORK INTEGRATION ---
    app.ue4ss_card = StandardCard(left_container, title="UE4SS SCRIPTING FRAMEWORK", icon="⚙️")
    app.ue4ss_card.pack(fill="x", padx=0)

    ue4ss_inner = InnerCard(app.ue4ss_card)
    ue4ss_inner.pack(fill="x", padx=15, pady=(0, 15))

    app.lbl_ue4ss_status = ctk.CTkLabel(
        ue4ss_inner, 
        text="Status: Scanning...", 
        font=("Segoe UI", 12, "bold"), 
        text_color="#9CA3AF"
    )
    app.lbl_ue4ss_status.pack(anchor="w", padx=20, pady=(15, 6))

    app.lbl_ue4ss_path = ctk.CTkLabel(
        ue4ss_inner, 
        text="Target: No path specified", 
        font=("Segoe UI", 10), 
        text_color="#9CA3AF"
    )
    app.lbl_ue4ss_path.pack(anchor="w", padx=20, pady=(0, 15))

    btn_action_frame = ctk.CTkFrame(ue4ss_inner, fg_color="transparent")
    btn_action_frame.pack(fill="x", padx=20, pady=(0, 15))

    app.btn_install_ue4ss = ctk.CTkButton(
        btn_action_frame,
        text="INSTALL UE4SS",
        fg_color=COLOR_NEON_BLUE,
        hover_color="#00B3CC",
        text_color="#08080A",
        font=("Segoe UI", 11, "bold"),
        height=32,
        command=lambda: trigger_ue4ss_installation(app)
    )
    app.btn_install_ue4ss.pack(side="left", fill="x", expand=True, padx=(0, 5))

    app.btn_uninstall_ue4ss = ctk.CTkButton(
        btn_action_frame,
        text="UNINSTALL",
        fg_color="#16161F",
        hover_color=COLOR_NEON_PINK,
        border_color=COLOR_NEON_PINK,
        border_width=1,
        text_color=COLOR_NEON_PINK,
        font=("Segoe UI", 11, "bold"),
        height=32,
        command=lambda: trigger_ue4ss_uninstallation(app)
    )
    app.btn_uninstall_ue4ss.pack(side="right", fill="x", expand=True, padx=(5, 0))

    # --- LEFT CONTAINER: MOD FILE DEPLOYER ---
    deploy_card = StandardCard(left_container, title="DEPLOY NEW MODIFICATION", icon="📦")
    deploy_card.pack(fill="x", padx=0)

    deploy_inner = InnerCard(deploy_card)
    deploy_inner.pack(fill="x", padx=15, pady=(0, 15))

    ctk.CTkLabel(
        deploy_inner, 
        text="Drop local .pak or mod .zip files here to auto-deploy:", 
        font=("Segoe UI", 11, "bold"), 
        text_color="#E2E8F0"
    ).pack(anchor="w", padx=20, pady=(10, 0))

    app.ent_mod_filepath = ctk.CTkEntry(
        deploy_inner, 
        placeholder_text="C:/path/to/my_mod.pak", 
        font=("Segoe UI", 11),
        fg_color="#101014",
        border_color="#1F2937",
        height=32
    )
    app.ent_mod_filepath.pack(fill="x", padx=20, pady=(15, 6))

    file_action_frame = ctk.CTkFrame(deploy_inner, fg_color="transparent")
    file_action_frame.pack(fill="x", padx=20, pady=(5, 15))

    btn_browse_mod = ctk.CTkButton(
        file_action_frame,
        text="BROWSE MOD FILE",
        fg_color="#16161F",
        hover_color="#1F2937",
        border_color=COLOR_NEON_BLUE,
        border_width=1,
        text_color=COLOR_NEON_BLUE,
        font=("Segoe UI", 11, "bold"),
        height=32,
        command=lambda: browse_mod_file(app)
    )
    btn_browse_mod.pack(side="left", fill="x", expand=True, padx=(0, 5))

    btn_deploy_mod = ctk.CTkButton(
        file_action_frame,
        text="DEPLOY SNAPSHOT",
        fg_color=COLOR_NEON_BLUE,
        hover_color="#00B3CC",
        text_color="#08080A",
        font=("Segoe UI", 11, "bold"),
        height=32,
        command=lambda: execute_mod_deployment(app)
    )
    btn_deploy_mod.pack(side="right", fill="x", expand=True, padx=(5, 0))

    # --- RIGHT CONTAINER: MOD REGISTRY LISTING & SELECTION HEADER ---
    registry_card = StandardCard(right_container, title="INSTALLED MODS REGISTRY", icon="📋")
    registry_card.pack(fill="both", expand=True, padx=0)

    # Action Controller Sub-Bar (For select all, deselect all, export list, and mass deletion)
    control_frame = ctk.CTkFrame(registry_card, fg_color="transparent")
    control_frame.pack(fill="x", padx=20, pady=(10, 10))

    # Batch selection handlers (Packed left)
    app.btn_select_all = ctk.CTkButton(
        control_frame,
        text="SELECT ALL",
        width=90,
        height=28,
        fg_color="#16161F",
        hover_color="#1F2937",
        border_color="#1F2937",
        border_width=1,
        text_color="#E2E8F0",
        font=("Segoe UI", 10, "bold"),
        command=lambda: select_all_mods(app, True)
    )
    app.btn_select_all.pack(side="left", padx=(0, 5))

    app.btn_deselect_all = ctk.CTkButton(
        control_frame,
        text="DESELECT ALL",
        width=100,
        height=28,
        fg_color="#16161F",
        hover_color="#1F2937",
        border_color="#1F2937",
        border_width=1,
        text_color="#E2E8F0",
        font=("Segoe UI", 10, "bold"),
        command=lambda: select_all_mods(app, False)
    )
    app.btn_deselect_all.pack(side="left", padx=5)

    # Massive actions (Packed right)
    app.btn_export_list = ctk.CTkButton(
        control_frame,
        text="EXPORT LIST",
        width=100,
        height=28,
        fg_color="#16161F",
        hover_color="#1F1F2A",
        border_color=COLOR_NEON_BLUE,
        border_width=1,
        text_color=COLOR_NEON_BLUE,
        font=("Segoe UI", 10, "bold"),
        command=lambda: export_mod_list(app)
    )
    app.btn_export_list.pack(side="right", padx=(5, 0))

    app.btn_mass_delete = ctk.CTkButton(
        control_frame,
        text="DELETE SELECTED",
        width=120,
        height=28,
        fg_color="#16161F",
        hover_color="#2A161A",
        border_color=COLOR_NEON_PINK,
        border_width=1,
        text_color=COLOR_NEON_PINK,
        font=("Segoe UI", 10, "bold"),
        command=lambda: mass_delete_mods(app)
    )
    app.btn_mass_delete.pack(side="right", padx=5)

    # Frame containing the listing
    app.mods_registry_container = ctk.CTkScrollableFrame(
        registry_card,
        fg_color="#060608",
        border_color="#1F2937",
        border_width=1,
        height=400
    )
    app.mods_registry_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Run initial scanning routines
    update_mods_tab_ui(app)

def check_ue4ss_installed(base_dir):
    """Checks if the RE-UE4SS framework binaries exist in the Palworld installation."""
    if not base_dir:
        return False
    bin_dir = Path(base_dir) / "Pal/Binaries/Win64"
    return (bin_dir / "UE4SS.dll").exists()

def update_mods_tab_ui(app):
    """Scans framework binaries and installed pak/lua mods, updating the UI accordingly."""
    if not app.base_dir:
        app.lbl_ue4ss_status.configure(text="Status: Offline (Set Server Path First)", text_color=COLOR_NEON_PINK)
        app.lbl_ue4ss_path.configure(text="Target: No directory selected.")
        app.btn_install_ue4ss.configure(state="disabled")
        app.btn_uninstall_ue4ss.configure(state="disabled")
        app.btn_select_all.configure(state="disabled")
        app.btn_deselect_all.configure(state="disabled")
        app.btn_export_list.configure(state="disabled")
        app.btn_mass_delete.configure(state="disabled")
        clear_registry_view(app, "Please configure your Server Path in the main dashboard first.")
        return

    app.btn_install_ue4ss.configure(state="normal")
    app.btn_select_all.configure(state="normal")
    app.btn_deselect_all.configure(state="normal")
    app.btn_export_list.configure(state="normal")
    app.btn_mass_delete.configure(state="normal")
    
    bin_dir = Path(app.base_dir) / "Pal/Binaries/Win64"
    app.lbl_ue4ss_path.configure(text=f"Target: .../Win64/")

    if check_ue4ss_installed(app.base_dir):
        app.lbl_ue4ss_status.configure(text="Status: Installed (RE-UE4SS Framework Active)", text_color="#2ecc71")
        app.btn_uninstall_ue4ss.configure(state="normal")
    else:
        app.lbl_ue4ss_status.configure(text="Status: Not Installed", text_color=COLOR_NEON_PINK)
        app.btn_uninstall_ue4ss.configure(state="disabled")

    # Refresh the list registry
    render_installed_mods(app)

def clear_registry_view(app, message=""):
    """Wipes the scrollable frame of the registry listing."""
    for child in app.mods_registry_container.winfo_children():
        child.destroy()
    if message:
        lbl = ctk.CTkLabel(
            app.mods_registry_container, 
            text=message, 
            font=("Segoe UI", 11, "italic"), 
            text_color="#9CA3AF"
        )
        lbl.pack(pady=40)

def render_installed_mods(app):
    """Scans and renders all .pak mods and UE4SS plugins."""
    clear_registry_view(app)
    app.selected_mods_vars = {}  # Flush cached trackers prior to redraw

    # 1. Define paths
    base = Path(app.base_dir)
    pak_mods_dir = base / "Pal/Content/Paks/~mods"
    ue4ss_mods_dir = base / "Pal/Binaries/Win64/Mods"

    mod_list = []

    # A. Scan Pak Mods (~mods folder)
    if pak_mods_dir.exists():
        for item in pak_mods_dir.iterdir():
            if item.is_file() and item.suffix.lower() in [".pak", ".disabled"]:
                is_enabled = item.suffix.lower() == ".pak"
                mod_list.append({
                    "name": item.name.replace(".disabled", ""),
                    "type": "Pak Mod (.pak)",
                    "path": item,
                    "enabled": is_enabled
                })

    # B. Scan Lua/UE4SS Mods
    if ue4ss_mods_dir.exists():
        # Exclude official or framework dependencies from showing as customizable mods
        exclusions = {"shared", "gotostartlocalserver", "custom_sources", "perfect_tracking"}
        for item in ue4ss_mods_dir.iterdir():
            if item.is_dir() and item.name.lower() not in exclusions:
                is_disabled = item.name.endswith(".disabled")
                clean_name = item.name.replace(".disabled", "")
                mod_list.append({
                    "name": clean_name,
                    "type": "Lua Plugin (UE4SS)",
                    "path": item,
                    "enabled": not is_disabled
                })

    if not mod_list:
        clear_registry_view(app, "No mods or scripting plugins detected in installation directories.")
        return

    # Render each mod inside a clean inner-card row layout
    for i, mod in enumerate(mod_list):
        row_frame = ctk.CTkFrame(
            app.mods_registry_container, 
            fg_color="#101014", 
            border_color="#1F2937", 
            border_width=1, 
            corner_radius=6
        )
        row_frame.pack(fill="x", padx=10, pady=4)

        # Batch Selection Checkbox (Saves state in application dictionary mapped to absolute filepaths)
        chk_var = ctk.BooleanVar(value=False)
        app.selected_mods_vars[str(mod["path"])] = chk_var
        
        chk_box = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=chk_var,
            width=24,
            checkbox_width=18,
            checkbox_height=18,
            border_color="#1F2937",
            hover_color="#1F1F2A",
            fg_color=COLOR_NEON_BLUE,
            checkmark_color="#08080A"
        )
        chk_box.pack(side="left", padx=(15, 0))

        # Labels
        lbl_mod_name = ctk.CTkLabel(
            row_frame, 
            text=mod["name"], 
            font=("Segoe UI", 11, "bold"), 
            text_color="#E2E8F0"
        )
        lbl_mod_name.pack(side="left", padx=(10, 15), pady=8)

        lbl_mod_type = ctk.CTkLabel(
            row_frame, 
            text=f"[{mod['type']}]", 
            font=("Segoe UI", 10, "italic"), 
            text_color=COLOR_NEON_BLUE
        )
        lbl_mod_type.pack(side="left", padx=10)

        # Toggle Switch
        switch_var = ctk.BooleanVar(value=mod["enabled"])
        switch_toggle = ctk.CTkSwitch(
            row_frame,
            text="ACTIVE" if mod["enabled"] else "DISABLED",
            font=("Segoe UI", 10, "bold"),
            text_color="#2ecc71" if mod["enabled"] else COLOR_NEON_PINK,
            progress_color="#2ecc71",
            variable=switch_var,
            command=lambda m=mod, v=switch_var: toggle_mod_state(app, m, v.get())
        )
        switch_toggle.pack(side="right", padx=10)

def toggle_mod_state(app, mod_data, turn_on):
    """Enables or disables a mod package by swapping extensions or directory markers."""
    path = Path(mod_data["path"])
    try:
        if mod_data["type"] == "Pak Mod (.pak)":
            if turn_on and path.suffix == ".disabled":
                new_path = path.with_suffix(".pak")
                path.rename(new_path)
            elif not turn_on and path.suffix == ".pak":
                new_path = path.with_suffix(".disabled")
                path.rename(new_path)
        else:
            # For directory mods (UE4SS), toggle using directory suffix modification
            if turn_on and path.name.endswith(".disabled"):
                new_name = path.name.replace(".disabled", "")
                new_path = path.parent / new_name
                path.rename(new_path)
            elif not turn_on and not path.name.endswith(".disabled"):
                new_name = f"{path.name}.disabled"
                new_path = path.parent / new_name
                path.rename(new_path)

        app.log(f"Mod state updated: {mod_data['name']} -> {'Enabled' if turn_on else 'Disabled'}")
    except Exception as e:
        messagebox.showerror("IO Error", f"Failed to modify mod status on disk:\n{e}")
    finally:
        update_mods_tab_ui(app)

def delete_mod_registry_item(app, path):
    """Permanently deletes a mod or plugin from the server filesystem."""
    if not messagebox.askyesno("Confirm Deletion", "This will permanently delete this mod configuration. Proceed?"):
        return
    try:
        p = Path(path)
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        app.log(f"Mod artifact deleted: {p.name}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clean mod files: {e}")
    finally:
        update_mods_tab_ui(app)

# --- BATCH ACTIONS & SELECTION CONTROLLERS ---

def select_all_mods(app, state=True):
    """Toggles select checkboxes across all scanned registry items."""
    if hasattr(app, "selected_mods_vars") and app.selected_mods_vars:
        for var in app.selected_mods_vars.values():
            var.set(state)

def mass_delete_mods(app):
    """Permanently removes all chosen mods and directories inside a safe batch cleanup cycle."""
    if not hasattr(app, "selected_mods_vars") or not app.selected_mods_vars:
        return

    # Extract checked paths
    selected_paths = [Path(path_str) for path_str, var in app.selected_mods_vars.items() if var.get()]
    if not selected_paths:
        messagebox.showwarning("Selection Alert", "No mods are currently selected for batch deletion!")
        return

    confirm_msg = f"You are about to permanently delete {len(selected_paths)} selected mod(s) from the server.\n\nAre you sure you want to proceed?"
    if not messagebox.askyesno("Confirm Batch Deletion", confirm_msg):
        return

    deleted_count = 0
    failed_count = 0

    for path in selected_paths:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            app.log(f"Batch clean successfully purged: {path.name}")
            deleted_count += 1
        except Exception as e:
            app.log(f"Failed to delete mod artifact {path.name}: {e}")
            failed_count += 1

    if failed_count > 0:
        messagebox.showwarning("Batch Execution Finished", f"Successfully cleaned {deleted_count} mod(s).\nFailed to clean {failed_count} mod(s) (check execution log).")
    else:
        messagebox.showinfo("Success", f"Successfully deleted all {deleted_count} selected mod(s)!")

    update_mods_tab_ui(app)

def export_mod_list(app):
    """Compiles a text file of installed pak/lua mods and their active states for multiplayer sharing."""
    if not app.base_dir:
        return

    base = Path(app.base_dir)
    pak_mods_dir = base / "Pal/Content/Paks/~mods"
    ue4ss_mods_dir = base / "Pal/Binaries/Win64/Mods"

    paks = []
    luas = []

    # Compile structures
    if pak_mods_dir.exists():
        for item in pak_mods_dir.iterdir():
            if item.is_file() and item.suffix.lower() in [".pak", ".disabled"]:
                is_enabled = item.suffix.lower() == ".pak"
                status = "ACTIVE" if is_enabled else "DISABLED"
                paks.append(f"- {item.name.replace('.disabled', '')} [Pak Mod] ({status})")

    if ue4ss_mods_dir.exists():
        exclusions = {"shared", "gotostartlocalserver", "custom_sources", "perfect_tracking"}
        for item in ue4ss_mods_dir.iterdir():
            if item.is_dir() and item.name.lower() not in exclusions:
                is_disabled = item.name.endswith(".disabled")
                status = "ACTIVE" if not is_disabled else "DISABLED"
                luas.append(f"- {item.name.replace('.disabled', '')} [Lua Plugin] ({status})")

    # Build report layout
    lines = [
        "==================================================",
        "       PALWORLD SERVER INSTALLED MOD LIST         ",
        "==================================================",
        f"Exported On: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Server Path: {base}",
        "--------------------------------------------------\n",
        "[PAK MODIFICATIONS]"
    ]

    if paks:
        lines.extend(paks)
    else:
        lines.append("(No Pak mods installed)")

    lines.append("\n[UE4SS LUA SCRIPT PLUGINS]")
    if luas:
        lines.extend(luas)
    else:
        lines.append("(No Lua plugins installed)")

    lines.append("\n==================================================")
    lines.append("Share this file with your players to coordinate configurations!")

    # Prompt file save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        initialfile="palworld_server_mods.txt",
        title="Export Installed Mods Configuration List"
    )

    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            app.log(f"Mod configuration list successfully exported to: {Path(file_path).name}")
            messagebox.showinfo("Success", "Server mod list exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save exported file to target path:\n{e}")

# --- FILE PATHING & EXPLORER UTILS ---

def browse_mod_file(app):
    """Displays open file dialog selecting either pak or zip extensions."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Palworld Mod Archives", "*.pak;*.zip"), ("Pak Files", "*.pak"), ("Zip Archives", "*.zip")]
    )
    if file_path:
        app.ent_mod_filepath.delete(0, "end")
        app.ent_mod_filepath.insert(0, file_path)

def execute_mod_deployment(app):
    """Unpacks or copies chosen files to proper content directories with smart zip inspection."""
    path_str = app.ent_mod_filepath.get().strip()
    if not path_str or not app.base_dir:
        messagebox.showwarning("Execution Warn", "Please specify both server base directory and a valid mod file!")
        return

    source = Path(path_str)
    if not source.exists():
        messagebox.showerror("Error", "Specified local file does not exist!")
        return

    try:
        base = Path(app.base_dir)
        if source.suffix.lower() == ".pak":
            # Direct raw pak file copy
            dest_dir = base / "Pal/Content/Paks/~mods"
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, dest_dir / source.name)
            app.log(f"Deployed Pak Mod: {source.name} successfully.")
            messagebox.showinfo("Success", "Pak Mod successfully injected into ~mods directory!")
            
        elif source.suffix.lower() == ".zip":
            # Open the zip to inspect the contents dynamically
            with zipfile.ZipFile(source, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # Check if there are any .pak files inside this zip
                pak_files = [f for f in file_list if f.lower().endswith('.pak')]
                
                if pak_files:
                    # Treat as standard Pak Mod packaged inside a zip!
                    dest_dir = base / "Pal/Content/Paks/~mods"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    extracted_count = 0
                    for pak_file in pak_files:
                        filename = Path(pak_file).name
                        if filename: # Skip folder structure definitions
                            with zip_ref.open(pak_file) as source_file:
                                with open(dest_dir / filename, "wb") as target_file:
                                    shutil.copyfileobj(source_file, target_file)
                            extracted_count += 1
                            
                    app.log(f"Extracted and deployed {extracted_count} Pak Mod(s) from zip into ~mods successfully.")
                    messagebox.showinfo("Success", f"Extracted and deployed {extracted_count} Pak Mod(s) to ~mods!")
                else:
                    # Treat as UE4SS Lua script plugin
                    if not check_ue4ss_installed(app.base_dir):
                        if not messagebox.askyesno("UE4SS Alert", "Deploying custom Lua plugin but UE4SS isn't installed. Deploy anyway?"):
                            return
                            
                    dest_dir = base / "Pal/Binaries/Win64/Mods"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    zip_ref.extractall(dest_dir)
                    app.log(f"Extracted Lua plugins to: .../Win64/Mods/")
                    messagebox.showinfo("Success", "Lua mod successfully extracted to UE4SS Mods folder!")

        app.ent_mod_filepath.delete(0, "end")
    except Exception as e:
        messagebox.showerror("IO Exception", f"Failed to transfer files: {e}")
    except zipfile.BadZipFile:
        messagebox.showerror("Archive Error", "The file specified is corrupted or is not a valid zip archive.")
    finally:
        update_mods_tab_ui(app)

# --- AUTOMATED UE4SS LIFECYCLE CONTROLLERS ---

def trigger_ue4ss_installation(app):
    """Starts safe installation routine on dedicated background daemon thread."""
    if not app.base_dir:
        return
    app.btn_install_ue4ss.configure(state="disabled", text="QUERYING GITHUB...")
    app.log("Contacting RE-UE4SS GitHub releases API...")
    threading.Thread(target=installation_worker, args=(app,), daemon=True).start()

def installation_worker(app):
    """Background worker fetching and extracting stable RE-UE4SS frameworks."""
    try:
        bin_dir = Path(app.base_dir) / "Pal/Binaries/Win64"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Pull the absolute latest download URL dynamically
        download_url, tag_name = get_latest_ue4ss_download_url()
        app.log(f"Latest release found on GitHub: {tag_name}")
        app.after(0, lambda: app.btn_install_ue4ss.configure(text="DOWNLOADING..."))
        
        zip_path = bin_dir / f"UE4SS_{tag_name}.zip"

        # 1. Fetch framework
        req = urllib.request.Request(
            download_url,
            headers={'User-Agent': 'PalworldServerManager-Client/1.0'}
        )
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        app.log("Framework zip pulled. Extracting files...")

        # 2. Extract contents directly to executing path
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(str(bin_dir))

        # 3. Clean local file
        zip_path.unlink()
        app.log(f"RE-UE4SS Framework ({tag_name}) successfully deployed to Win64 binaries folder.")
        app.after(0, lambda: messagebox.showinfo("Success", f"RE-UE4SS Framework {tag_name} successfully installed!"))
    except Exception as e:
        app.after(0, lambda: messagebox.showerror("API Error", f"Failed to download UE4SS framework: {e}"))
    finally:
        app.after(0, lambda: app.btn_install_ue4ss.configure(state="normal", text="INSTALL UE4SS"))
        app.after(0, lambda: update_mods_tab_ui(app))

def trigger_ue4ss_uninstallation(app):
    """Removes all RE-UE4SS framework DLLs and associated configs from Binaries directory."""
    if not messagebox.askyesno("Confirm Removal", "This will delete the UE4SS system and its configured mods folder. Continue?"):
        return

    try:
        bin_dir = Path(app.base_dir) / "Pal/Binaries/Win64"
        files_to_remove = ["UE4SS.dll", "UE4SS-settings.ini", "dwmapi.dll"]
        dirs_to_remove = ["Mods"]

        for f in files_to_remove:
            target = bin_dir / f
            if target.exists():
                target.unlink()

        for d in dirs_to_remove:
            target = bin_dir / d
            if target.exists():
                shutil.rmtree(target)

        app.log("Successfully wiped UE4SS frameworks and associated binaries.")
        messagebox.showinfo("Success", "RE-UE4SS framework successfully uninstalled!")
    except Exception as e:
        messagebox.showerror("Cleanup Exception", f"Failed to clean files cleanly: {e}")
    finally:
        update_mods_tab_ui(app)