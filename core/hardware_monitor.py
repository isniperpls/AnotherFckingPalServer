# ==============================================================================
# core/hardware_monitor.py
# Hardware Monitor Module (Optimized for Windows 11 AMD & Intel)
# Uses a multi-tier approach to fetch precise CPU, RAM, Disk, and Temp stats.
# Supports automatic drive-mounting detection and delta network I/O speed checking.
# ==============================================================================

import os
import subprocess
import shutil
import time

try:
    import psutil
except ImportError:
    psutil = None

class HardwareMonitor:
    # State tracking variables for network throughput calculation
    _last_sent = 0
    _last_recv = 0
    _last_time = 0.0

    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage."""
        if not psutil:
            return 0.0
        return psutil.cpu_percent(interval=None)

    @staticmethod
    def get_ram_usage():
        """Returns system RAM metrics."""
        if not psutil:
            return {"percent": 0.0, "used_gb": 0.0, "total_gb": 0.0}
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024**3), 2),
            "total_gb": round(mem.total / (1024**3), 2)
        }

    @staticmethod
    def get_disk_usage(path_str):
        """
        Returns disk usage metrics for the drive containing the server path.
        Automatically auto-detects if PalServer is running on another drive partition.
        """
        try:
            detected_path = None
            if psutil:
                # Scan active processes for any running PalServer instance to locate its volume
                for proc in psutil.process_iter(['name', 'exe']):
                    try:
                        if proc.info['name'] and proc.info['name'].lower() in ["palserver.exe", "palserver-win64-test.exe", "palserver-win64-shipping.exe"]:
                            exe_path = proc.info['exe']
                            if exe_path and os.path.exists(exe_path):
                                detected_path = os.path.abspath(exe_path)
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

            # Resolve evaluation path priority: Process Executable Drive > Selected Path > C:\
            target_path = "C:\\"
            if detected_path:
                target_path = detected_path
            elif path_str:
                target_path = os.path.abspath(path_str)

            usage = shutil.disk_usage(target_path)
            total_gb = round(usage.total / (1024**3), 2)
            used_gb = round(usage.used / (1024**3), 2)
            percent = round((usage.used / usage.total) * 100, 1)

            # Extract the raw drive letters cleanly (e.g. "D:" or "C:")
            drive = os.path.splitdrive(target_path)[0]
            if not drive:
                drive = "C:"

            return {
                "percent": percent,
                "used_gb": used_gb,
                "total_gb": total_gb,
                "drive": drive.upper()
            }
        except Exception:
            return {"percent": 0.0, "used_gb": 0.0, "total_gb": 0.0, "drive": "C:"}

    @staticmethod
    def get_network_speed():
        """
        Calculates current network speeds (Up / Down) in KB/s based on delta bytes.
        Also tracks absolute cumulative sent and received data in Gigabytes.
        """
        if not psutil:
            return {"sent_speed_kb": 0.0, "recv_speed_kb": 0.0, "total_sent_gb": 0.0, "total_recv_gb": 0.0}
            
        now = time.time()
        try:
            net_io = psutil.net_io_counters()
            sent = net_io.bytes_sent
            recv = net_io.bytes_recv
        except Exception:
            return {"sent_speed_kb": 0.0, "recv_speed_kb": 0.0, "total_sent_gb": 0.0, "total_recv_gb": 0.0}

        sent_speed = 0.0
        recv_speed = 0.0
        
        # Calculate delta throughput speeds divided by elapsed time
        if HardwareMonitor._last_time > 0:
            dt = now - HardwareMonitor._last_time
            if dt > 0:
                sent_speed = (sent - HardwareMonitor._last_sent) / dt
                recv_speed = (recv - HardwareMonitor._last_recv) / dt

        HardwareMonitor._last_sent = sent
        HardwareMonitor._last_recv = recv
        HardwareMonitor._last_time = now
        
        return {
            "sent_speed_kb": round(sent_speed / 1024, 1),
            "recv_speed_kb": round(recv_speed / 1024, 1),
            "total_sent_gb": round(sent / (1024**3), 2),
            "total_recv_gb": round(recv / (1024**3), 2)
        }

    @staticmethod
    def get_cpu_temp():
        """
        Queries CPU temperature on Windows 11 using a robust 3-Tier fallback system.
        Works seamlessly on both AMD and Intel platforms.
        """
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # ----------------------------------------------------------------------
        # TIER 1: LibreHardwareMonitor / OpenHardwareMonitor WMI Bridge (Gold Standard)
        # ----------------------------------------------------------------------
        try:
            cmd_lhm = (
                "PowerShell -Command \""
                "Get-CimInstance -Namespace root/LibreHardwareMonitor -ClassName Sensor "
                "| Where-Object { $_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU Package*' } "
                "| Select-Object -ExpandProperty Value\""
            )
            process = subprocess.Popen(cmd_lhm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, startupinfo=startupinfo)
            stdout, _ = process.communicate()
            output = stdout.decode().strip()
            if output:
                return f"{round(float(output.split()[0]), 1)}°C"
        except Exception:
            pass

        try:
            cmd_ohm = (
                "PowerShell -Command \""
                "Get-WmiObject -Namespace root/OpenHardwareMonitor -Class Sensor "
                "| Where-Object { $_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU Package*' } "
                "| Select-Object -ExpandProperty Value\""
            )
            process = subprocess.Popen(cmd_ohm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, startupinfo=startupinfo)
            stdout, _ = process.communicate()
            output = stdout.decode().strip()
            if output:
                return f"{round(float(output.split()[0]), 1)}°C"
        except Exception:
            pass

        # ----------------------------------------------------------------------
        # TIER 2: Native ACPI Thermal Zone Query (Requires Administrator Privileges)
        # ----------------------------------------------------------------------
        try:
            cmd_acpi = "PowerShell -Command \"Get-WmiObject -Namespace root/wmi -Class MSAcpi_ThermalZoneTemperature | Select-Object -ExpandProperty CurrentTemperature\""
            process = subprocess.Popen(cmd_acpi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, startupinfo=startupinfo)
            stdout, _ = process.communicate()
            output = stdout.decode().strip()
            lines = output.split()
            if lines and lines[0].isdigit():
                temp_c = (float(lines[0]) / 10.0) - 273.15
                if 10 < temp_c < 115:
                    return f"{round(temp_c, 1)}°C"
        except Exception:
            pass

        # ----------------------------------------------------------------------
        # TIER 3: Generic CIM Temperature Sensor Check
        # ----------------------------------------------------------------------
        try:
            cmd_cim = "PowerShell -Command \"Get-CimInstance -ClassName Win32_TemperatureSensor | Select-Object -ExpandProperty CurrentReading\""
            process = subprocess.Popen(cmd_cim, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, startupinfo=startupinfo)
            stdout, _ = process.communicate()
            output = stdout.decode().strip()
            if output and output.isdigit():
                return f"{output}°C"
        except Exception:
            pass

        return "N/A"

    @staticmethod
    def get_process_ram_usage(pid):
        """Returns physical RAM usage (in GB) of a specific process ID."""
        if not psutil or not pid:
            return 0.0
        try:
            proc = psutil.Process(pid)
            return round(proc.memory_info().rss / (1024**3), 2)
        except Exception:
            return 0.0