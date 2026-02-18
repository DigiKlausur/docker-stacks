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
c = get_config() # type: ignore # noqa: F821

backup_enabled = os.getenv("E2X_BACKUP_ENABLED", "false").lower() in ("true", "1")

def parse_int_env_var(var_name: str) -> int | None:
    value_str = os.getenv(var_name)
    if value_str:
        try:
            return int(value_str)
        except ValueError:
            pass

if backup_enabled:
    if os.getenv("E2X_BACKUP_DIR"):
        c.E2xBackupApp.backup_dir = os.getenv("E2X_BACKUP_DIR")

    max_files = parse_int_env_var("E2X_BACKUP_MAX_FILES")
    if max_files is not None:
        c.E2xBackupApp.max_backup_files = max_files
    max_size_mb = parse_int_env_var("E2X_BACKUP_MAX_SIZE_MB")
    if max_size_mb is not None:
        c.E2xBackupApp.max_backup_size_mb = max_size_mb
    min_seconds = parse_int_env_var("E2X_MIN_SECONDS_BETWEEN_BACKUPS")
    if min_seconds is not None:
        c.E2xBackupApp.min_seconds_between_backups = min_seconds
