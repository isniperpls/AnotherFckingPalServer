# ==============================================================================
# core/scheduler.py
# Scheduler Module
# Handles automated restart timing, custom warning intervals, and broadcast execution.
# ==============================================================================

import threading
import time
import requests

class RestartScheduler:
    def __init__(self, app_instance):
        self.app = app_instance
        self.timer_active = False
        self.seconds_remaining = 0
        self.warnings = [] # List of dicts: {"offset_sec": int, "message": str, "sent": bool}
        self.timer_thread = None
        
        # State preservation variables for repeating cycles
        self.total_seconds_duration = 0
        self.custom_warnings_cache = []
        self.repeat_active = False

    def start_scheduler(self, total_seconds, custom_warnings, repeat_active=False):
        """
        Starts the countdown timer.
        custom_warnings: List of dicts with keys 'offset_sec' and 'message'
        """
        self.cancel_scheduler() # Clear any existing timer
        
        self.total_seconds_duration = total_seconds
        self.custom_warnings_cache = custom_warnings
        self.repeat_active = repeat_active
        
        self.seconds_remaining = total_seconds
        self.timer_active = True
        
        # Reset warnings state
        self.warnings = []
        for w in custom_warnings:
            if w['offset_sec'] < total_seconds:
                self.warnings.append({
                    "offset_sec": w['offset_sec'],
                    "message": w['message'],
                    "sent": False
                })
        
        self.app.log(f"Auto-restart scheduler started. Duration: {total_seconds // 60} minutes.")
        self.timer_thread = threading.Thread(target=self._run_countdown, daemon=True)
        self.timer_thread.start()

    def cancel_scheduler(self):
        if self.timer_active:
            self.timer_active = False
            self.seconds_remaining = 0
            self.warnings = []
            self.repeat_active = False
            self.app.log("Reboot scheduler cancelled.")
            
        # Reset status elements thread-safely
        self.app.after(0, lambda: self.app.update_scheduler_label("Next Restart: Disabled", "#e74c3c"))
        self.app.after(0, lambda: self.app.update_scheduler_progress(0.0))

    def _run_countdown(self):
        while self.timer_active and self.seconds_remaining > 0:
            h = self.seconds_remaining // 3600
            m = (self.seconds_remaining % 3600) // 60
            s = self.seconds_remaining % 60
            countdown_str = f"Next Restart in: {h:02d}:{m:02d}:{s:02d}"
            
            # Symmetrically calculate timeline progress percent values (from 0.0 to 1.0)
            progress = 1.0
            if self.total_seconds_duration > 0:
                progress = 1.0 - (self.seconds_remaining / self.total_seconds_duration)
            
            self.app.after(0, lambda s=countdown_str: self.app.update_scheduler_label(s, "#1f6aa5"))
            self.app.after(0, lambda p=progress: self.app.update_scheduler_progress(p))
            self._check_warnings()

            time.sleep(1)
            self.seconds_remaining -= 1

        if self.timer_active and self.seconds_remaining <= 0:
            self.timer_active = False
            self.app.after(0, lambda: self.app.update_scheduler_label("Rebooting server...", "#e74c3c"))
            self.app.after(0, lambda: self.app.update_scheduler_progress(1.0))
            self._trigger_restart()

    def _check_warnings(self):
        api_enabled, api_port, admin_password, _ = self.app._get_api_config()
        
        # Absolute package path fix to support root execution context
        from core.metrics_controller import is_server_running_on_system
        if not is_server_running_on_system(self.app):
            return # Server is offline, no need to broadcast warnings
            
        for w in self.warnings:
            if not w['sent'] and self.seconds_remaining <= w['offset_sec']:
                w['sent'] = True
                msg = w['message']
                self.app.log(f"Sending scheduled warning broadcast: '{msg}'")
                if api_enabled:
                    threading.Thread(
                        target=self._send_broadcast, 
                        args=(api_port, admin_password, msg), 
                        daemon=True
                    ).start()

    def _send_broadcast(self, port, password, message):
        url = f"http://127.0.0.1:{port}/v1/api/announce"
        payload = {"message": message}
        try:
            requests.post(url, json=payload, auth=('admin', password), timeout=3)
        except Exception as e:
            self.app.log(f"Scheduled broadcast failed: {e}")

    def _trigger_restart(self):
        api_enabled, api_port, admin_password, _ = self.app._get_api_config()
        # Absolute package path fix to support root execution context
        from core.metrics_controller import is_server_running_on_system
        
        def run_seq():
            self.app.log("Executing scheduled restart sequence...")
            if is_server_running_on_system(self.app):
                if api_enabled:
                    self.app.log("Broadcasting final reboot shutdown notice...")
                    try:
                        requests.post(f"http://127.0.0.1:{api_port}/v1/api/announce", json={"message": "Server rebooting now!"}, auth=('admin', admin_password), timeout=2)
                    except: pass
                    
                    self.app.log("Issuing automated safe world save command...")
                    try:
                        requests.post(f"http://127.0.0.1:{api_port}/v1/api/save", auth=('admin', admin_password), timeout=5)
                        self.app.log("Automated save complete.")
                    except Exception as e:
                        self.app.log(f"Automated save query failed: {e}")
                    time.sleep(2)
                
                # Shutdown
                self.app.log("Stopping active game engine process...")
                self.app.after(0, self.app.shutdown_server_process)
                time.sleep(8) # Allow taskkill tree plenty of time to release ports
            else:
                self.app.log("Server process was already offline.")
            
            # Start up
            self.app.log("Executing server restart-up boot cycle...")
            self.app.after(0, self.app.start_server_process)
            
            # Symmetrical wait loop for launch sequence verification
            self.app.log("Waiting for game engine initialization...")
            time.sleep(10)
            
            if self.repeat_active:
                self.app.log("Repeat schedule enabled. Triggering next restart countdown...")
                self.app.after(0, lambda: self.start_scheduler(
                    self.total_seconds_duration, 
                    self.custom_warnings_cache, 
                    repeat_active=True
                ))
            else:
                self.app.log("Automated restart routine completed successfully.")
                self.app.after(0, lambda: self.app.update_scheduler_label("Next Restart: Disabled", "#e74c3c"))
                self.app.after(0, lambda: self.app.update_scheduler_progress(0.0))

        threading.Thread(target=run_seq, daemon=True).start()