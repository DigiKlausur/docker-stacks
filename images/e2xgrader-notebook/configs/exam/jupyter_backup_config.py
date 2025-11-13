"""
e2x-jupyter-backup configuration file.

This uses the environment variables:
- E2X_BACKUP_ENABLED: Whether the backup functionality is enabled (default: false)
- E2X_BACKUP_DIR: The directory where backups are stored relative to the notebook (default: '.backup')
- E2X_BACKUP_MAX_FILES: The maximum number of backup files to keep per notebook (default: 10)
"""

import os
from e2x_jupyter_backup import get_post_save_hook
c = get_config() # noqa: F821

backup_enabled = os.getenv("E2X_BACKUP_ENABLED", "false").lower() in ("true", "1")

if backup_enabled == "true":
    if os.getenv("E2X_BACKUP_DIR"):
        c.E2xBackupApp.backup_dir = os.getenv("E2X_BACKUP_DIR")
    if os.getenv("E2X_BACKUP_MAX_FILES"):
        c.E2xBackupApp.max_backup_files = int(os.getenv("E2X_BACKUP_MAX_FILES"))
    c.FileContentsManager.post_save_hook = get_post_save_hook()
