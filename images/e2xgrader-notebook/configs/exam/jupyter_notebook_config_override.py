##############################################################
# Jupyter Notebook configuration override for exam mode      #
# Will be appended to the default jupyter_notebook_config.py #
# when E2XGRADER_MODE=student_exam                           #
##############################################################
import os

backup_enabled = os.getenv("E2X_BACKUP_ENABLED", "false").lower() in ("true", "1")

if backup_enabled:
    from e2x_jupyter_backup import get_post_save_hook # type: ignore
    c.FileContentsManager.post_save_hook = get_post_save_hook() # type: ignore  # noqa: F821
