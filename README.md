Another Fcking Server Manager (AFSM)

Another Fcking Server Manager (AFSM) is a Python-based graphical administration utility for managing Palworld Dedicated Servers on Windows systems. Built on CustomTkinter, the manager acts as an integrated control panel wrapping process lifecycles, configuration editing, automated save-state backups, live map tracking, metric polling, and mod deployments.

The application utilizes non-blocking background threads (Python threading.Thread) for all heavy IO, network API, and file manipulation tasks to ensure the main GUI thread remains responsive.

🛠️ Functional Capabilities & Features

1. Process & Server Lifecycle Management

Asynchronous SteamCMD Automation: Downloads, installs, and updates dedicated server binaries by spawning SteamCMD via subprocess.Popen. It monitors stdout asynchronously and routes live installation output directly to the system logs.

Process Detection: Tracks running server processes via psutil. It can monitor both server instances launched directly through the manager and external processes matching palserver.exe or its variants.

System Hardware Monitoring: Dynamically queries CPU load, RAM usage, and disk storage metrics. It employs a multi-tiered temperature extraction fallback (WMI, MSFT, and generic CIM classes) to gather processor temperatures on various Windows platforms.

2. Viewport-Optimized Live Map Tracking

Resource-Efficient Map Renderer: Designed to handle $4000 \times 4000$ pixel map assets without CPU bottlenecks. On redraw (_refresh), the map view calculates the current visible bounding box, crops only that specific area from the original image in memory, and resizes only that cropped region. This reduces Pillow scaling operations by up to 95%, maintaining fluid framerates during zoom and pan actions.

Dynamic Resampling Toggles: Temporarily switches Pillow's resampler to NEAREST mode during live dragging and zooming to eliminate scaling latency. Once the user stops interacting, it automatically reapplies the higher-quality BILINEAR anti-aliasing filter.

Affine Coordinate Mapping: Maps raw Unreal Engine 3D world coordinates directly to 2D image coordinates. It resolves shearing and rotation issues by applying a solved 2D affine transformation:

$$px\_ratio = \frac{0.0027584259 \cdot X_{UE} + 0.0000024262355 \cdot Y_{UE} + 2036.7778}{4000.0}$$

$$py\_ratio = \frac{-0.0000099881 \cdot X_{UE} - 0.0027527692 \cdot Y_{UE} + 1243.0266}{4000.0}$$

This provides sub-pixel player tracking across the entire playable boundaries of the map.

Cursor-Centric Zoom: Keeps the exact unscaled coordinate under the mouse cursor stationary during zooming, matching standard map navigation behavior.

3. Automated Backup & Restore System

Interval Backups: Automates ZIP-compressed saves folder snapshots on a background daemon thread based on custom time intervals.

Boot & Shutdown Snapshots: Automatically triggers save snapshots immediately before process startup and upon receiving a termination signal, protecting against data loss from crashes.

Saves Management: Provides a structured list of available historical archives, displaying file size, creation timestamp, and local path. Restoration works by stopping the server, cleaning current save directories, and extracting the chosen ZIP archive back to /Pal/Saved.

4. Automated Restart Scheduler

Tiered Warning Alert System: Sends custom-timed warning alerts to active players using the server's REST API /v1/api/announce endpoint prior to triggering a restart.

Graceful Database Saves: Before killing the server, the scheduler executes a forced /v1/api/save request to flush dirty memory pages to disk, monitors the save state, safely terminates the process trees, and automatically boots the process back up.

Loop Options: Includes toggles for repeating restart schedules indefinitely.

5. Detailed Engine Metrics Polling

High-Frequency REST Polling: Queries /v1/api/metrics via HTTP GET requests on a background thread to retrieve live server performance data.

Engine Telemetry Gauges: Extracts and displays raw server frames-per-second (FPS) and tick calculation times (in milliseconds) with scaling progress meters.

World Stats Analytics: Tracks active player counts against the max limit, total in-game days elapsed, and active base camp locations.

Historical Logging: Appends live telemetry states with timestamps to an internal text window, creating a local, scrollable performance log.

6. Mods & Plugins Administrator

Asynchronous RE-UE4SS Installer: Queries the public GitHub API (releases/latest) on a background thread to find the latest tagged RE-UE4SS framework zip, downloads it, and extracts the core DLLs and configurations straight to Pal/Binaries/Win64.

Smart ZIP Inspector: On mod deployment, the manager opens .zip archives in memory to inspect filenames before copying:

If .pak files are present, it extracts only the .pak elements directly to the Pal/Content/Paks/~mods folder.

If no .pak files exist, it treats the archive as a Lua plugin and extracts the files to Pal/Binaries/Win64/Mods.

Registry Toggles: Disables or enables active mods by renaming directories/files with a .disabled extension.

Batch Actions: Supports multi-selection checkboxes for bulk-purging active modifications or compiling structured text summaries of installed mods for multiplayer sharing.

7. Player Moderation Panel

Live Session Tracking: Displays currently authenticated players side-by-side with historical logs.

Moderation Tools: Quick buttons execute announcements, kicks, bans, or unban commands over REST.

Roster Exporter: Writes current player listings to local formatted sheets.

8. Save Data Migration Converter

GUID Relocation: Translates local Single-player or Co-Op .sav save files over to a Dedicated Server format by decoding the compressed binary stream (via zlib), replacing host player GUID headers, re-compressing, and exporting the converted files.

📁 Project Architecture

AFSM utilizes a structured MVC division of components:

main.py - Main GUI setup, tab configuration, and window lifecycle.

configs/ - Storage folder for user preferences, player logs, and configuration data.

core/backup_manager.py - ZIP compression, deletion, and save state restorations.

core/config_manager.py - Configuration loader/writer for JSON-based preferences.

core/hardware_monitor.py - System resource checks, network delta speed, and temperature metrics.

core/metrics_controller.py - Background HTTP loops querying players list and metrics endpoints.

core/scheduler.py - Timer countdown loops, warning intervals, and restart logic.

core/server_controller.py - Process startups, taskkill execution, and API actions.

core/ui_components.py - Central CTK UI classes, Scrollable frames, and custom Cards.

views/backups_view.py - File restoration grid and custom directories mapping.

views/converter_view.py - Save file translation configuration elements.

views/dashboard_view.py - Vitals gauges, console log stream, and SteamCMD execution.

views/header_view.py - Logo panel, path config, power controls, and optional support link.

views/map_view.py - Optimized map canvas, zoom, and player plotting.

views/metrics_view.py - Detailed engine performance meters and logs.

views/mods_view.py - Mod installer, smart ZIP analyzer, exporter, and multi-selection checkboxes.

views/player_view.py - Online/Offline rosters, kick, ban, and admin logs.

views/scheduler_view.py - Dynamic restart timings and warning triggers.

views/settings_view.py - Integrated PalWorldSettings.ini editor.

🚀 Getting Started

System Prerequisites

OS: Windows 10 or Windows 11

Language: Python 3.10 or higher

Required Libraries:

pip install customtkinter requests psutil pillow



Running the Manager

Clone this repository locally, navigate to the directory, and run the following command:

python main.py



⚖️ License

This project is licensed under the permissive MIT License. It grants full rights to copy, modify, distribute, and sell the software under the condition that the copyright notice and liability disclaimer are included. See the LICENSE file for details
