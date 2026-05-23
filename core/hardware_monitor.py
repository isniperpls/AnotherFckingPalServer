# ==============================================================================
# core/hardware_monitor.py
# Hardware Monitor Module - Temperature Removed
# Optimized for real-time Windows 10/11 telemetry.
# ==============================================================================

import os
import shutil
import time

try:
    import psutil
except ImportError:
    psutil = None

class HardwareMonitor:
    _last_sent = 0
    _last_recv = 0
    _last_time = 0.0

    @staticmethod
    def get_cpu_usage():
        """Returns live CPU usage using psutil."""
        if not psutil: return 0.0
        return psutil.cpu_percent(interval=None)

    @staticmethod
    def get_ram_usage():
        """Returns system RAM metrics."""
        if not psutil: return {"percent": 0.0, "used_gb": 0.0, "total_gb": 0.0}
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024**3), 2),
            "total_gb": round(mem.total / (1024**3), 2)
        }

    @staticmethod
    def get_disk_usage(path_str):
        """Returns disk usage for the server drive."""
        try:
            usage = shutil.disk_usage(path_str if path_str else "C:\\")
            return {
                "percent": round((usage.used / usage.total) * 100, 1),
                "used_gb": round(usage.used / (1024**3), 2),
                "total_gb": round(usage.total / (1024**3), 2)
            }
        except:
            return {"percent": 0.0, "used_gb": 0.0, "total_gb": 0.0}

    @staticmethod
    def get_network_speed():
        """Calculates delta network throughput."""
        if not psutil: return {"sent_speed_kb": 0.0, "recv_speed_kb": 0.0}
        now = time.time()
        try:
            net_io = psutil.net_io_counters()
            sent, recv = net_io.bytes_sent, net_io.bytes_recv
        except: return {"sent_speed_kb": 0.0, "recv_speed_kb": 0.0}

        sent_speed = recv_speed = 0.0
        if HardwareMonitor._last_time > 0:
            dt = now - HardwareMonitor._last_time
            if dt > 0:
                sent_speed = (sent - HardwareMonitor._last_sent) / dt
                recv_speed = (recv - HardwareMonitor._last_recv) / dt

        HardwareMonitor._last_sent, HardwareMonitor._last_recv, HardwareMonitor._last_time = sent, recv, now
        return {
            "sent_speed_kb": round(sent_speed / 1024, 1),
            "recv_speed_kb": round(recv_speed / 1024, 1)
        }

    @staticmethod
    def get_process_ram_usage(pid):
        """Live RAM usage for PalServer."""
        if not psutil or not pid: return 0.0
        try:
            return round(psutil.Process(pid).memory_info().rss / (1024**3), 2)
        except: return 0.0