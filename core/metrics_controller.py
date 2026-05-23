# ==============================================================================
# core/metrics_controller.py
# Metrics Controller Module
# Handles background polling threads to query metrics without locking the UI thread.
# ==============================================================================

import threading
import time
import requests
import psutil

# Corrected absolute import to pull the HardwareMonitor class
from core.hardware_monitor import HardwareMonitor

def is_server_running_on_system(app):
    """Checks if the PalServer process is running, either managed or externally."""
    # 1. Check managed process
    if app.server_process and app.server_process.poll() is None:
        return True
    
    # 2. Scan active Windows system processes for external launches
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() in ["palserver.exe", "palserver-win64-test.exe", "palserver-win64-shipping.exe"]:
                return True
    except Exception:
        pass
    return False

def get_palserver_pid():
    """Finds and returns the active PID of PalServer.exe on the system."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].lower() in ["palserver.exe", "palserver-win64-test.exe", "palserver-win64-shipping.exe"]:
                return proc.info['pid']
    except Exception:
        pass
    return None

def start_background_loops(app):
    """Initiates daemon threads to pull performance and connection metrics."""
    threading.Thread(target=_monitor_metrics_loop, args=(app,), daemon=True).start()
    threading.Thread(target=_monitor_hardware_loop, args=(app,), daemon=True).start()

def _monitor_metrics_loop(app):
    """Infinite loop querying the official Palworld REST API for active players and detailed engine metrics."""
    while True:
        running = is_server_running_on_system(app)
        
        # Synchronize UI button state dynamically
        app.after(0, lambda r=running: app.update_server_status_ui(r))

        if running:
            api_enabled, api_port, admin_password, max_players = app._get_api_config()
            if api_enabled:
                # Symmetrical safety check: Admin password cannot be empty in Palworld for REST API to boot
                if not admin_password:
                    app.after(0, lambda: app.set_player_ui_error("AdminPassword is blank! REST API requires an AdminPassword."))
                    app.after(0, lambda: app.set_detailed_metrics_error("AdminPassword is blank"))
                else:
                    # Thread safety fallback block: Query both players and engine-level metrics endpoints
                    auth_tuple = ('admin', admin_password)
                    
                    # 1. Player List Extraction
                    players_url = f"http://127.0.0.1:{api_port}/v1/api/players"
                    try:
                        response = requests.get(players_url, auth=auth_tuple, timeout=2)
                        if response.status_code == 200:
                            data = response.json()
                            players = data.get("players", [])
                            count = len(players)
                            app.after(0, lambda p=players, c=count, m=max_players: app.update_player_ui(p, c, m))
                        elif response.status_code == 401:
                            app.after(0, lambda: app.set_player_ui_error("REST API Unauthorized (401). Check your AdminPassword!"))
                        else:
                            app.after(0, lambda status=f"API Error (HTTP {response.status_code})": app.set_player_ui_error(status))
                    except requests.exceptions.RequestException:
                        app.after(0, lambda: app.set_player_ui_error("Waiting for REST API connection... Is port forwarded?"))

                    # 2. Detailed Engine Metrics Extraction
                    metrics_url = f"http://127.0.0.1:{api_port}/v1/api/metrics"
                    try:
                        metrics_res = requests.get(metrics_url, auth=auth_tuple, timeout=2)
                        if metrics_res.status_code == 200:
                            metrics_data = metrics_res.json()
                            app.after(0, lambda d=metrics_data: app.update_detailed_metrics(d))
                        elif metrics_res.status_code == 401:
                            app.after(0, lambda: app.set_detailed_metrics_error("REST API Unauthorized (401)"))
                        else:
                            app.after(0, lambda: app.set_detailed_metrics_error(f"HTTP {metrics_res.status_code}"))
                    except requests.exceptions.RequestException:
                        app.after(0, lambda: app.set_detailed_metrics_error("Offline"))
            else:
                app.after(0, lambda: app.set_player_ui_error("REST API disabled in options."))
                app.after(0, lambda: app.set_detailed_metrics_error("REST API Disabled"))
        else:
            app.after(0, lambda: app.set_player_ui_error("Server process is offline."))
            app.after(0, lambda: app.set_detailed_metrics_error("Server Process Offline"))
        time.sleep(4)

def _monitor_hardware_loop(app):
    """Infinite loop pulling diagnostics from the hardware_monitor module."""
    while True:
        try:
            cpu_pct = HardwareMonitor.get_cpu_usage()
            cpu_temp = HardwareMonitor.get_cpu_temp()
            ram_data = HardwareMonitor.get_ram_usage()
            
            base_dir_str = str(app.base_dir) if app.base_dir else "C:\\"
            disk_data = HardwareMonitor.get_disk_usage(base_dir_str)
            net_data = HardwareMonitor.get_network_speed() # Queried network throughput
            
            palserver_ram_str = "PalServer RAM: Offline"
            system_pid = get_palserver_pid()
            if system_pid:
                p_ram = HardwareMonitor.get_process_ram_usage(system_pid)
                palserver_ram_str = f"PalServer RAM: {p_ram} GB"
                
            # Safely hand off cpu, temperature, ram, disk, and network variables to the GUI
            app.after(
                0, 
                lambda c=cpu_pct, t=cpu_temp, r=ram_data, d=disk_data, p=palserver_ram_str, n=net_data: 
                app.update_hardware_ui(c, t, r, d, p, n)
            )
        except Exception as e:
            print(f"[Metrics Loop Error] Hardware monitoring failure: {e}")
        time.sleep(2)