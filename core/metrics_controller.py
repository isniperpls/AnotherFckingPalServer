# ==============================================================================
# core/metrics_controller.py
# Metrics Controller Module - Temperature Removed
# Handles telemetry loops without blocking the GUI.
# ==============================================================================

import threading
import time
import psutil
import requests
from core.hardware_monitor import HardwareMonitor

def is_server_running_on_system(app):
    """Checks if the PalServer process is alive."""
    if app.server_process and app.server_process.poll() is None:
        return True
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and "palserver" in proc.info['name'].lower():
                return True
    except: pass
    return False

def get_palserver_pid():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and "palserver" in proc.info['name'].lower():
                return proc.info['pid']
    except: pass
    return None

def start_background_loops(app):
    """Starts the telemetry threads."""
    # Hardware stats loop (2 second interval)
    threading.Thread(target=_monitor_hardware_loop, args=(app,), daemon=True).start()
    # REST API loop (4 second interval)
    threading.Thread(target=_monitor_api_loop, args=(app,), daemon=True).start()

def _monitor_hardware_loop(app):
    while True:
        try:
            cpu = HardwareMonitor.get_cpu_usage()
            ram = HardwareMonitor.get_ram_usage()
            net = HardwareMonitor.get_network_speed()
            
            path = str(app.base_dir) if app.base_dir else "C:\\"
            disk = HardwareMonitor.get_disk_usage(path)
            
            p_ram = "Offline"
            pid = get_palserver_pid()
            if pid:
                p_ram = f"{HardwareMonitor.get_process_ram_usage(pid)} GB"
            
            # Send to UI thread (Temperature parameter removed)
            app.after(0, lambda c=cpu, r=ram, d=disk, p=p_ram, n=net: 
                      app.update_hardware_ui(c, r, d, p, n))
            
        except Exception as e:
            print(f"Hardware Loop Error: {e}")
        
        time.sleep(2)

def _monitor_api_loop(app):
    while True:
        running = is_server_running_on_system(app)
        app.after(0, lambda r=running: app.update_server_status_ui(r))
        
        if running:
            api_enabled, api_port, admin_password, max_players = app._get_api_config()
            if api_enabled and admin_password:
                auth = ('admin', admin_password)
                try:
                    # Player List
                    r = requests.get(f"http://127.0.0.1:{api_port}/v1/api/players", auth=auth, timeout=2)
                    if r.status_code == 200:
                        players = r.json().get("players", [])
                        app.after(0, lambda p=players, c=len(players), m=max_players: app.update_player_ui(p, c, m))
                    
                    # Detailed Metrics
                    m_res = requests.get(f"http://127.0.0.1:{api_port}/v1/api/metrics", auth=auth, timeout=2)
                    if m_res.status_code == 200:
                        app.after(0, lambda d=m_res.json(): app.update_detailed_metrics(d))
                except: pass
        else:
            app.after(0, lambda: app.set_player_ui_error("Offline"))
            app.after(0, lambda: app.set_detailed_metrics_error("Offline"))
            
        time.sleep(4)