# ==============================================================================
# core/backup_manager.py
# Backup Management Logic
# ==============================================================================

import os
import shutil
import zipfile
import time
from pathlib import Path

class BackupManager:
    @staticmethod
    def get_backups_list(base_dir, custom_dir=None):
        """Scans the backup directory for existing archives."""
        search_dir = Path(custom_dir) if custom_dir else (base_dir / "Saved_Backups")
        if not search_dir.exists():
            return []
            
        backups = []
        for file in search_dir.glob("*.zip"):
            stat = file.stat()
            backups.append({
                "name": file.name,
                "path": str(file),
                "size": f"{stat.st_size / 1024 / 1024:.2f} MB",
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
            })
        return sorted(backups, key=lambda x: x["date"], reverse=True)

    @staticmethod
    def create_backup(base_dir, log_func, custom_dir=None, server_name="Palworld_Server"):
        """Compresses world saves into a unique, timestamped, and counter-indexed archive."""
        save_dir = base_dir / "Pal/Saved/SaveGames/0"
        backup_root = Path(custom_dir) if custom_dir else (base_dir / "Saved_Backups")
        backup_root.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M")
        
        # Calculate unique counter to prevent overwrites
        counter = 1
        base_name = f"{server_name}_Backup_{timestamp}"
        target_zip = backup_root / f"{base_name}.zip"
        
        while target_zip.exists():
            target_zip = backup_root / f"{base_name}-{counter}.zip"
            counter += 1

        try:
            log_func(f"Generating automated backup: {target_zip.name}...")
            with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(save_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(base_dir / "Pal/Saved")
                        zipf.write(file_path, arcname)
            log_func(f"Backup created successfully: {target_zip.name}")
        except Exception as e:
            log_func(f"Backup Error: {str(e)}")

    @staticmethod
    def delete_backup(path):
        """Removes a specific archive."""
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    @staticmethod
    def restore_backup(base_dir, zip_path, log_func):
        """Extracts an archive back into the server directory."""
        try:
            log_func(f"Restoring backup: {Path(zip_path).name}...")
            save_path = base_dir / "Pal/Saved"
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(save_path)
            
            log_func("Restore complete. Please restart the server.")
        except Exception as e:
            log_func(f"Restore Error: {str(e)}")