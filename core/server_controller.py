# ==============================================================================
# core/server_controller.py
# Server Operational Controller
# Manages process lifecycles, API configurations, and custom CLI shell arguments.
# ==============================================================================

import subprocess
import requests
import re
import time
import threading
import shlex
from pathlib import Path
from tkinter import messagebox

# Core dependency references
from core.backup_manager import BackupManager
from core.metrics_controller import is_server_running_on_system, get_palserver_pid

class ServerController:
    @staticmethod
    def get_api_config(app):
        """Retrieves active REST API values for background API thread validation with robust INI fallback."""
        api_enabled = False
        api_port = 8212
        admin_password = ""
        server_max_players = 32
        
        # 1. Attempt to read directly from the rendered UI Settings elements
        try:
            if "RESTAPIEnabled" in app.setting_entries:
                api_enabled = app.setting_entries["RESTAPIEnabled"].get() == "True"
            if "RESTAPIPort" in app.setting_entries:
                api_port = int(app.setting_entries["RESTAPIPort"].get())
            if "AdminPassword" in app.setting_entries:
                admin_password = app.setting_entries["AdminPassword"].get().replace('"', '')
            if "ServerPlayerMaxNum" in app.setting_entries:
                server_max_players = int(app.setting_entries["ServerPlayerMaxNum"].get())
            return api_enabled, api_port, admin_password, server_max_players
        except Exception:
            pass

        # 2. Fallback: Parse the INI directly if UI elements aren't initialized yet
        if app.base_dir:
            config_path = app.base_dir / "Pal/Saved/Config/WindowsServer/PalWorldSettings.ini"
            if config_path.exists():
                try:
                    content = config_path.read_text()
                    enabled_match = re.search(r"RESTAPIEnabled=(True|False)", content)
                    port_match = re.search(r"RESTAPIPort=(\d+)", content)
                    pass_match = re.search(r'AdminPassword="([^"]*)"', content)
                    max_match = re.search(r"ServerPlayerMaxNum=(\d+)", content)
                    
                    if enabled_match: api_enabled = enabled_match.group(1) == "True"
                    if port_match: api_port = int(port_match.group(1))
                    if pass_match: admin_password = pass_match.group(1)
                    if max_match: server_max_players = int(max_match.group(1))
                except Exception:
                    pass

        return api_enabled, api_port, admin_password, server_max_players

    @staticmethod
    def start_server_process(app):
        """Launches the dedicated game server executable with parsed CLI flags."""
        if is_server_running_on_system(app): 
            return
            
        exe = app.base_dir / "PalServer.exe" if app.base_dir else None
        if not exe or not exe.exists():
            app.log("Failed to start: Invalid directory or PalServer.exe missing.")
            return
        
        # Symmetrical Startup Automated Lifecycle Backup
        app.log("Generating automated server startup save-state backup...")
        BackupManager.create_backup(
            base_dir=app.base_dir, 
            log_func=app.log, 
            custom_dir=str(app.backup_dir) if app.backup_dir else None, 
            server_name=app.get_server_name()
        )
        
        # Local import to prevent circular dependency chains
        from views.backups_view import update_backups_list_ui
        app.after(0, lambda: update_backups_list_ui(app))

        # Base execution command array construction
        cmd = [str(exe)]

        # Fetch custom CLI parameters safely from the UI textbox field context
        if hasattr(app, "ent_launch_args") and app.ent_launch_args:
            args_raw = app.ent_launch_args.get().strip()
            if args_raw:
                try:
                    # Use shlex to split arguments safely respecting quoted strings
                    parsed_flags = shlex.split(args_raw)
                    cmd.extend(parsed_flags)
                    app.log(f"Appending custom launch flags: {parsed_flags}")
                except Exception as e:
                    app.log(f"[CLI Error] Arguments parsing failed: {e}. Falling back to default execution.")

        app.log("Launching server process...")
        app.server_process = subprocess.Popen(
            cmd, 
            cwd=str(app.base_dir), 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        app.btn_toggle.configure(text="STOP SERVER", fg_color="#FF3366", hover_color="#CC0033", text_color="#FFFFFF")
        app.log("Server started.")

    @staticmethod
    def shutdown_server_process(app):
        """Terminates the server process tree cleanly after running a safe shutdown backup."""
        pid = app.server_process.pid if app.server_process else get_palserver_pid()
        if pid:
            # 1. Pre-Shutdown Save Data Write Request
            api_enabled, api_port, admin_password, _ = ServerController.get_api_config(app)
            if api_enabled:
                app.log("Triggering world save via REST API before shutdown...")
                try:
                    url = f"http://127.0.0.1:{api_port}/v1/api/save"
                    response = requests.post(url, auth=('admin', admin_password), timeout=5)
                    if response.status_code == 200:
                        app.log("World save command issued successfully. Allowing IO buffer time...")
                        time.sleep(2)  # Give the game server time to write the files
                    else:
                        app.log(f"REST API save command failed with HTTP {response.status_code}")
                except Exception as e:
                    app.log(f"REST API save command timeout or connection failure: {e}")

            # 2. Symmetrical Shutdown Automated Lifecycle Backup
            if app.base_dir:
                app.log("Generating automated server shutdown save-state backup...")
                BackupManager.create_backup(
                    base_dir=app.base_dir, 
                    log_func=app.log, 
                    custom_dir=str(app.backup_dir) if app.backup_dir else None, 
                    server_name=app.get_server_name()
                )
                
                from views.backups_view import update_backups_list_ui
                app.after(0, lambda: update_backups_list_ui(app))

            # 3. Hard Process Termination
            app.log(f"Killing active server process tree (PID: {pid})...")
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)], 
                capture_output=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            app.server_process = None
            app.btn_toggle.configure(text="START SERVER", fg_color="#00E5FF", hover_color="#00B4CC", text_color="#08080A")
            app.log("Server terminated.")
        else:
            app.log("No running server process detected to terminate.")

    @staticmethod
    def toggle_server(app):
        """Toggles the active execution state of the game server."""
        if is_server_running_on_system(app): 
            ServerController.shutdown_server_process(app)
        else: 
            ServerController.start_server_process(app)

    @staticmethod
    def execute_player_api_action(app, endpoint, payload, action_name):
        """Helper to send standardized administrative actions asynchronously to the REST API."""
        api_enabled, api_port, admin_password, _ = app._get_api_config()
        if not is_server_running_on_system(app):
            messagebox.showwarning("Warning", "Server is not currently running.")
            return
        if not api_enabled:
            messagebox.showwarning("REST API Disabled", "Please enable 'RESTAPIEnabled' inside settings first!")
            return

        def run():
            url = f"http://127.0.0.1:{api_port}/v1/api/{endpoint}"
            try:
                response = requests.post(url, json=payload, auth=('admin', admin_password), timeout=5)
                if response.status_code == 200:
                    app.log(f"Successfully executed {action_name} for ID: {payload.get('userId')}")
                    messagebox.showinfo("Success", f"Player {action_name} executed successfully.")
                    
                    if action_name in ["Kick", "Ban"] and getattr(app, "selected_player_uid", None) == payload.get("userId"):
                        app.selected_player_uid = None
                        app.selected_player_name = None
                        app.lbl_selected_player.configure(text="No Player Selected", font=("Segoe UI", 12, "italic"), text_color="gray")
                        app.lbl_selected_uid.configure(text="ID: N/A", text_color="gray")
                else:
                    app.log(f"Failed {action_name} command. Status code: {response.status_code}")
                    messagebox.showerror("Error", f"Command failed with status code: {response.status_code}")
            except Exception as e:
                app.log(f"REST API connection failure for {action_name}: {e}")
                messagebox.showerror("Connection Error", f"Failed to contact REST API: {e}")

        threading.Thread(target=run, daemon=True).start()

    @staticmethod
    def send_announcement(app):
        """Broadcasts a raw string chat notification to all active players."""
        msg = app.ent_announcement.get().strip()
        if not msg: 
            return
            
        api_enabled, api_port, admin_password, _ = app._get_api_config()
        if not is_server_running_on_system(app):
            messagebox.showwarning("Warning", "Server is not running. Please start the server first!")
            return
        if not api_enabled:
            messagebox.showwarning("REST API Disabled", "Please enable 'RESTAPIEnabled' inside settings to use chat announcements!")
            return
            
        def do_post():
            url = f"http://127.0.0.1:{api_port}/v1/api/announce"
            try:
                response = requests.post(url, json={"message": msg}, auth=('admin', admin_password), timeout=3)
                if response.status_code == 200:
                    app.log(f"Broadcasted Chat Message: {msg}")
                    app.after(0, lambda: app.ent_announcement.delete(0, "end"))
                else:
                    app.log(f"Announcement failed: REST API returned HTTP {response.status_code}")
            except Exception as e:
                app.log(f"API Announcement connection failed: {e}")
                
        threading.Thread(target=do_post, daemon=True).start()