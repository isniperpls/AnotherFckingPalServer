Another Fcking Server Manager

A Windows-based graphical interface for managing Palworld dedicated servers. This tool simplifies server deployment, daily maintenance, and administrative tasks.

Features

Server Control: Start/stop the server and monitor current status via a real-time dashboard.

Settings Management: Graphical interface for editing PalWorldSettings.ini without manual file editing.

Backup Manager: Automated and manual backup creation, with restoration and deletion capabilities.

Player Management: View online players and perform kick/ban actions via the Palworld REST API.

Live Map Tracking: Interactive map overlay to track active player coordinates and world topology.

Mod Manager: Automates UE4SS framework installation and pak/lua mod deployment.

Restart Scheduler: Set automated restart intervals with configurable broadcast warnings.

System Metrics: Real-time monitoring of CPU usage, RAM, disk, and network throughput.

Prerequisites

Windows 10 or 11.

Python 3.x (if running from source).

Administrator privileges are recommended for network monitoring and proper process control.

Setup

Server Path: Upon launching for the first time, click "SET SERVER PATH" in the header to point the manager to your Palworld server directory.

Deployment: Use the "INSTALL / UPDATE" button on the Dashboard to download and configure SteamCMD in exe root and the Palworld Dedicated Server (App ID 2394010) into the selected server path.

Settings: Navigate to the "Server Settings" tab to configure your world parameters.

Launch: Return to the Dashboard and click "START SERVER."

Usage

API Configuration: To use Player Management and Metrics, set RESTAPIEnabled to True in the Server Settings tab and define an AdminPassword.

Map Tracking: Place map.jpg or map.png in the application root directory (where the executable or main script is located) to enable the live map overlay.

Backups: Enable automated backups in the "Backups Manager" tab to save your world state at specific intervals.

Development

This project is built using customtkinter for the GUI and psutil for system telemetry.
