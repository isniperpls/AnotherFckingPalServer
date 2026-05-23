# ==============================================================================
# main.py
# Another Fcking Server Manager - Main GUI Application
# ==============================================================================

import customtkinter as ctk
import tkinter as tk
import json
import time
import urllib.request
import zipfile
import subprocess
import threading
import sys
from pathlib import Path
from tkinter import messagebox, filedialog

from core.scheduler import RestartScheduler
from core.backup_manager import BackupManager
from core.metrics_controller import start_background_loops, is_server_running_on_system
from core.server_controller import ServerController
from core.config_manager import load_manager_config, save_manager_config
from core.ui_components import COLOR_DARK_BG, COLOR_NEON_BLUE, COLOR_NEON_PINK

from views.header_view import setup_header_bar
from views.dashboard_view import setup_dashboard_tab
from views.scheduler_view import setup_scheduler_tab
from views.settings_view import setup_settings_tab, load_settings_data, save_settings_data
from views.player_view import setup_player_tab, update_player_management_list
from views.backups_view import setup_backups_tab, update_backups_list_ui
from views.map_view import PalworldMapTab
from views.converter_view import setup_converter_tab
from views.metrics_view import setup_metrics_tab, update_metrics_ui, set_metrics_offline_ui
from views.mods_view import setup_mods_tab, update_mods_tab_ui

class PalManagerPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Another Fcking Server Manager")
        
        # Configure and center 1600x900 window geometry relative to the screen dimensions
        width = 1600
        height = 900
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate starting coordinates
        start_x = int((screen_width / 2) - (width / 2))
        start_y = int((screen_height / 2) - (height / 2))
        
        self.geometry(f"{width}x{height}+{start_x}+{start_y}")
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLOR_DARK_BG) 
        
        self.config_file = Path("configs/manager_config.json")
        self.config_data = load_manager_config()
        path_str = self.config_data.get("server_path", "")
        self.base_dir = Path(path_str) if path_str else None
        
        backup_path_str = self.config_data.get("backup_path", "")
        self.backup_dir = Path(backup_path_str) if backup_path_str else None
        
        try:
            self.backup_interval_mins = int(self.config_data.get("backup_interval_mins", 60))
        except (ValueError, TypeError):
            self.backup_interval_mins = 60
            
        self.auto_backup_enabled = bool(self.config_data.get("auto_backup_enabled", False))
        self.last_auto_backup_time = time.time()
        
        self.server_process = None
        self.setting_entries = {}
        self.scheduler = RestartScheduler(self)
        
        self.selected_player_uid = None
        self.selected_player_name = None

        self._setup_ui()
        
        initial_args = self.config_data.get("launch_args", "-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -NumberOfWorkerThreadsServer=8")
        if hasattr(self, "ent_launch_args") and self.ent_launch_args:
            self.ent_launch_args.insert(0, initial_args)

        if self.base_dir: 
            self.load_settings()

        start_background_loops(self)
        threading.Thread(target=self._auto_backup_loop, daemon=True).start()

    def _setup_ui(self):
        setup_header_bar(self)

        self.tabs = ctk.CTkTabview(
            self,
            segmented_button_selected_color=COLOR_NEON_BLUE,
            segmented_button_unselected_color="#101014",
            text_color="#E2E8F0",
            command=self._on_tab_change
        )
        self.tabs.pack(side="bottom", fill="both", expand=True, padx=25, pady=(15, 25))
        
        setup_dashboard_tab(self, self.tabs.add("Dashboard"))
        setup_player_tab(self, self.tabs.add("Player Management"))
        self.map_controller = PalworldMapTab(self.tabs.add("Live Map"))
        setup_backups_tab(self, self.tabs.add("Backups Manager"))
        setup_scheduler_tab(self, self.tabs.add("Scheduler"))
        setup_metrics_tab(self, self.tabs.add("Server Metrics"))
        setup_mods_tab(self, self.tabs.add("Mods Manager"))
        setup_settings_tab(self, self.tabs.add("Server Settings"))
        setup_converter_tab(self, self.tabs.add("Converter"))

    def _on_tab_change(self):
        """Callback triggered when the user switches tabs."""
        selected_tab = self.tabs.get()
        if selected_tab == "Backups Manager":
            update_backups_list_ui(self)
        elif selected_tab == "Mods Manager":
            update_mods_tab_ui(self)

    def save_manager_configs(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        launch_args_str = self.ent_launch_args.get().strip() if hasattr(self, "ent_launch_args") else ""
        
        sched_data = {}
        if hasattr(self, "ent_restart_hours"):
            sched_data = {
                "hours": self.ent_restart_hours.get().strip(),
                "mins": self.ent_restart_mins.get().strip(),
                "repeat": bool(self.cb_repeat_restart.get()),
                "warn1_min": getattr(self, "ent_warn1_min").get().strip() if hasattr(self, "ent_warn1_min") else "10",
                "warn1_msg": getattr(self, "ent_warn1_msg").get().strip() if hasattr(self, "ent_warn1_msg") else "Restart in 10m",
                "warn2_min": getattr(self, "ent_warn2_min").get().strip() if hasattr(self, "ent_warn2_min") else "5",
                "warn2_msg": getattr(self, "ent_warn2_msg").get().strip() if hasattr(self, "ent_warn2_msg") else "Restart in 5m",
                "warn3_min": getattr(self, "ent_warn3_min").get().strip() if hasattr(self, "ent_warn3_min") else "1",
                "warn3_msg": getattr(self, "ent_warn3_msg").get().strip() if hasattr(self, "ent_warn3_msg") else "Restart in 1m"
            }

        config_payload = {
            "server_path": str(self.base_dir) if self.base_dir else "",
            "backup_path": str(self.backup_dir) if self.backup_dir else "",
            "backup_interval_mins": self.backup_interval_mins,
            "auto_backup_enabled": self.auto_backup_enabled,
            "launch_args": launch_args_str,
            "scheduler_settings": sched_data
        }
        self.config_file.write_text(json.dumps(config_payload, indent=4))

    def load_stored_scheduler_settings(self):
        sched_data = self.config_data.get("scheduler_settings", {})
        if not sched_data: return
            
        def assign_val(attr, key, fallback):
            if hasattr(self, attr):
                widget = getattr(self, attr)
                widget.delete(0, "end")
                widget.insert(0, sched_data.get(key, fallback))

        assign_val("ent_restart_hours", "hours", "0")
        assign_val("ent_restart_mins", "mins", "30")
        assign_val("ent_warn1_min", "warn1_min", "10")
        assign_val("ent_warn1_msg", "warn1_msg", "Restart in 10m")
        assign_val("ent_warn2_min", "warn2_min", "5")
        assign_val("ent_warn2_msg", "warn2_msg", "Restart in 5m")
        assign_val("ent_warn3_min", "warn3_min", "1")
        assign_val("ent_warn3_msg", "warn3_msg", "Restart in 1m")

    def log(self, msg):
        if hasattr(self, "log_view"):
            self.log_view.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_view.see("end")

    def browse_path(self):
        selected = filedialog.askdirectory()
        if selected:
            self.base_dir = Path(selected)
            self.save_manager_configs()
            self.load_settings()

    def toggle_server(self): 
        ServerController.toggle_server(self)
        
    def start_server_process(self): 
        ServerController.start_server_process(self)
        
    def shutdown_server_process(self): 
        ServerController.shutdown_server_process(self)

    def load_settings(self):
        load_settings_data(self)
        update_backups_list_ui(self)
        self.update_backup_ui_states()

    def save_settings(self): 
        save_settings_data(self)

    def trigger_steamcmd_installation(self):
        if is_server_running_on_system(self):
            messagebox.showerror("Error", "Stop server first!")
            return
        if not self.base_dir:
            messagebox.showwarning("Error", "Set path first!")
            return
        if messagebox.askyesno("Confirm", "Download/Update server files?"):
            self.btn_install_server.configure(state="disabled", text="UPDATING...")
            threading.Thread(target=self._run_steamcmd_installation_worker, daemon=True).start()

    def _run_steamcmd_installation_worker(self):
        try:
            app_root = Path(sys.argv[0]).parent.absolute()
            steamcmd_root = app_root / "steamcmd"
            steamcmd_root.mkdir(parents=True, exist_ok=True)
            steamcmd_exe = steamcmd_root / "steamcmd.exe"
            
            if not steamcmd_exe.exists():
                urllib.request.urlretrieve("https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip", str(steamcmd_root / "steamcmd.zip"))
                with zipfile.ZipFile(steamcmd_root / "steamcmd.zip", 'r') as zf:
                    zf.extractall(str(steamcmd_root))

            cmd = [str(steamcmd_exe), "+force_install_dir", str(self.base_dir), "+login", "anonymous", "+app_update", "2394010", "validate", "+quit"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            while True:
                line = process.stdout.readline()
                if not line: break
                self.after(0, lambda l=line.strip(): self.log(f"[SteamCMD] {l}"))
            process.wait()
            self.after(0, self.load_settings)
        except Exception as e:
            self.after(0, lambda: self.log(f"Installer Error: {e}"))
        finally:
            self.after(0, lambda: self.btn_install_server.configure(state="normal", text="INSTALL / UPDATE"))

    def update_hardware_ui(self, cpu, temp, ram, disk, p_ram, net=None):
        if hasattr(self, "lbl_cpu_val"):
            self.lbl_cpu_val.configure(text=f"CPU: {cpu}% ({temp})")
            self.bar_cpu.set(cpu / 100.0)
            self.lbl_ram_val.configure(text=f"RAM: {ram['used_gb']}G / {ram['total_gb']}G")
            self.bar_ram.set(ram['percent'] / 100.0)
            self.lbl_disk_val.configure(text=f"Disk: {disk['used_gb']}G / {disk['total_gb']}G")
            self.bar_disk.set(disk['percent'] / 100.0)
            if net and hasattr(self, "lbl_net_val"):
                self.lbl_net_val.configure(text=f"Up: {net['sent_speed_kb']} KB/s | Down: {net['recv_speed_kb']} KB/s")

    def update_player_ui(self, players, count, max_players):
        if hasattr(self, "lbl_player_count"):
            self.lbl_player_count.configure(text=f"Players: {count}/{max_players}", text_color=COLOR_NEON_BLUE)
        update_player_management_list(self, players)
        if hasattr(self, "map_controller"):
            self.map_controller.update_player_positions(players)

    def set_player_ui_error(self, message):
        if hasattr(self, "lbl_player_count"):
            self.lbl_player_count.configure(text="Offline", text_color=COLOR_NEON_PINK)
        update_player_management_list(self, [])
        if hasattr(self, "map_controller"):
            self.map_controller.update_player_positions([])

    def update_detailed_metrics(self, data):
        """Standard routing to update detailed tab metrics."""
        update_metrics_ui(self, data)

    def set_detailed_metrics_error(self, error_msg):
        """Routing to update detailed metrics status on error."""
        set_metrics_offline_ui(self, error_msg)

    def update_server_status_ui(self, is_running):
        if hasattr(self, "btn_toggle"):
            if is_running:
                self.btn_toggle.configure(text="STOP SERVER", fg_color=COLOR_NEON_PINK)
                if hasattr(self, "lbl_quick_status_val"): self.lbl_quick_status_val.configure(text="ONLINE", text_color="#2ecc71")
            else:
                self.btn_toggle.configure(text="START SERVER", fg_color=COLOR_NEON_BLUE)
                if hasattr(self, "lbl_quick_status_val"): self.lbl_quick_status_val.configure(text="OFFLINE", text_color=COLOR_NEON_PINK)

    def update_scheduler_label(self, text, color):
        """Cleanly formats the scheduler string to prevent duplicate prefixes."""
        # Strip any redundant prefixes the core scheduler might send
        clean_text = text.replace("Next Restart in: ", "").replace("Next Restart: ", "").strip()
        
        # 1. Update the large label in the Scheduler Tab
        if hasattr(self, "lbl_restart_countdown"):
            if clean_text.lower() in ["disabled", "none", "cancelled"]:
                self.lbl_restart_countdown.configure(text="No Active Schedule", text_color=color)
            else:
                self.lbl_restart_countdown.configure(text=f"Next Restart in: {clean_text}", text_color=color)

        # 2. Update the smaller label in the Dashboard Tab
        if hasattr(self, "lbl_dashboard_restart_countdown"):
            self.lbl_dashboard_restart_countdown.configure(text=f"Next Restart in: {clean_text}", text_color=color)

    def update_scheduler_progress(self, value):
        if hasattr(self, "bar_restart_progress"): 
            self.bar_restart_progress.set(value)

    def _get_api_config(self): 
        return ServerController.get_api_config(self)
        
    def send_announcement(self): 
        ServerController.send_announcement(self)

    def kick_selected_player(self):
        if not self.selected_player_uid: return
        payload = {"userId": self.selected_player_uid, "message": getattr(self, "ent_admin_reason").get() or "Kicked"}
        ServerController.execute_player_api_action(self, "kick", payload, "Kick")

    def ban_selected_player(self):
        if not self.selected_player_uid: return
        payload = {"userId": self.selected_player_uid, "message": getattr(self, "ent_admin_reason").get() or "Banned"}
        ServerController.execute_player_api_action(self, "ban", payload, "Ban")

    def unban_selected_player(self):
        if not self.selected_player_uid: return
        ServerController.execute_player_api_action(self, "unban", {"userId": self.selected_player_uid}, "Unban")

    def get_server_name(self):
        if "ServerName" in self.setting_entries:
            return "".join(c for c in self.setting_entries["ServerName"].get() if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        return "Palworld_Server"

    def browse_backup_path(self):
        selected = filedialog.askdirectory()
        if selected:
            self.backup_dir = Path(selected)
            self.save_manager_configs()
            self.update_backup_ui_states()
            update_backups_list_ui(self)

    def toggle_auto_backup(self):
        self.auto_backup_enabled = bool(self.cb_auto_backup.get())
        self.save_manager_configs()
        self.last_auto_backup_time = time.time()

    def save_backup_interval(self):
        try:
            self.backup_interval_mins = int(self.ent_backup_interval.get())
            self.save_manager_configs()
            self.last_auto_backup_time = time.time()
        except: pass

    def update_backup_ui_states(self):
        if hasattr(self, "cb_auto_backup"):
            if self.auto_backup_enabled: self.cb_auto_backup.select()
            else: self.cb_auto_backup.deselect()
            self.ent_backup_interval.delete(0, "end")
            self.ent_backup_interval.insert(0, str(self.backup_interval_mins))
            
            if hasattr(self, "lbl_backup_path_val"):
                self.lbl_backup_path_val.configure(text=f"Current Path: {str(self.backup_dir) if self.backup_dir else 'Default (Saved_Backups)'}")

    def trigger_manual_backup(self):
        if not self.base_dir: 
            messagebox.showwarning("Warning", "Server path not set!")
            return
            
        if hasattr(self, "btn_trigger_backup"):
            self.btn_trigger_backup.configure(state="disabled", text="CREATING SNAPSHOT...")
            
        def _backup_worker():
            BackupManager.create_backup(self.base_dir, self.log, str(self.backup_dir) if self.backup_dir else None, self.get_server_name())
            self.after(0, lambda: update_backups_list_ui(self))
            if hasattr(self, "btn_trigger_backup"):
                self.after(0, lambda: self.btn_trigger_backup.configure(state="normal", text="CREATE INSTANT SNAPSHOT"))

        threading.Thread(target=_backup_worker, daemon=True).start()

    def trigger_backup_delete(self, path):
        if messagebox.askyesno("Delete", "Delete backup?"):
            BackupManager.delete_backup(path)
            update_backups_list_ui(self)

    def trigger_backup_restore(self, path):
        if is_server_running_on_system(self): return
        if messagebox.askyesno("Restore", "Overwrite current saves?"):
            threading.Thread(target=lambda: BackupManager.restore_backup(self.base_dir, path, self.log), daemon=True).start()

    def _auto_backup_loop(self):
        while True:
            if self.base_dir and self.auto_backup_enabled:
                if time.time() - self.last_auto_backup_time >= self.backup_interval_mins * 60:
                    BackupManager.create_backup(self.base_dir, self.log, str(self.backup_dir) if self.backup_dir else None, self.get_server_name())
                    self.last_auto_backup_time = time.time()
                    self.after(0, lambda: update_backups_list_ui(self))
            time.sleep(30)

    def schedule_restart(self):
        try:
            total = int(float(self.ent_restart_hours.get() or 0) * 3600 + float(self.ent_restart_mins.get() or 0) * 60)
            if total <= 0: return
            warns = []
            for i in range(1, 4):
                m = getattr(self, f"ent_warn{i}_min").get()
                msg = getattr(self, f"ent_warn{i}_msg").get()
                if m and msg: warns.append({"offset_sec": int(float(m)*60), "message": msg})
            self.scheduler.start_scheduler(total, warns, bool(self.cb_repeat_restart.get()))
        except: pass

    def cancel_restart(self): 
        self.scheduler.cancel_scheduler()

    def _validate_numeric(self, val):
        if val in ("", "-", "+", ".", "-.", "+."): return True
        try:
            float(val)
            return True
        except: return False

if __name__ == "__main__":
    app = PalManagerPro()
    app.mainloop()