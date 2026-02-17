"""
e2x-jupyter-backup configuration file.

This uses the environment variables:
- E2X_BACKUP_ENABLED: Whether the backup functionality is enabled (default: false)
- E2X_BACKUP_DIR: The directory where backups are stored relative to the notebook (default: '.backup')
- E2X_BACKUP_MAX_FILES: The maximum number of backup files to keep per notebook (default: 10)
- E2X_BACKUP_MAX_SIZE_MB: The maximum size of backup files in megabytes (default: 100)
- E2X_MIN_SECONDS_BETWEEN_BACKUPS: The minimum number of seconds between backups for the same notebook (default: 20)
"""

import os
c = get_config() # noqa: F821 # type: ignore

backup_enabled = os.getenv("E2X_BACKUP_ENABLED", "false").lower() in ("true", "1")

if backup_enabled:
    if os.getenv("E2X_BACKUP_DIR"):
        c.E2xBackupApp.backup_dir = os.getenv("E2X_BACKUP_DIR")
    if os.getenv("E2X_BACKUP_MAX_FILES"):
        try:
            c.E2xBackupApp.max_backup_files = int(os.getenv("E2X_BACKUP_MAX_FILES")) # type: ignore
        except ValueError:
            pass
    if os.getenv("E2X_BACKUP_MAX_SIZE_MB"):
        try:
            c.E2xBackupApp.max_backup_size_mb = int(os.getenv("E2X_BACKUP_MAX_SIZE_MB")) # type: ignore
        except ValueError:
            pass
    if os.getenv("E2X_MIN_SECONDS_BETWEEN_BACKUPS"):
        try:
            c.E2xBackupApp.min_seconds_between_backups = int(os.getenv("E2X_MIN_SECONDS_BETWEEN_BACKUPS")) # type: ignore
        except ValueError:
            pass
