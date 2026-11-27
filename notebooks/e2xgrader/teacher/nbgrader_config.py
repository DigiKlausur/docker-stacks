"""
nbgrader configuration for the teacher image: autograding runs in the Landlock
sandbox (autograde_sandbox.py). Installed to /opt/conda/etc/jupyter, so it loads
after /etc/jupyter/nbgrader_config.py (shared by all modes) and takes precedence.
A course's own nbgrader_config.py still loads last and could undo this.

This uses the environment variables:
- E2X_SHARED_PATHS: Colon-separated directories with shared materials. Autograded
  code may read them. Skipped, so the sandbox never exposes them: $HOME itself
  and its parents, hidden folders in $HOME (.ssh, .local, ...), and paths
  overlapping the course directory or the exchange.
- NBGRADER_COURSE_DIR, NBGRADER_EXCHANGE_DIR: see /etc/jupyter/nbgrader_config.py.

Errors in this file are only logged by nbgrader, and the file is then skipped,
leaving autograding unsandboxed. The Dockerfile therefore checks at build time
that the swap below is in place. Keep everything else here free of exceptions.
"""
import os
import sys

from e2xgrader.config import configure_base
from traitlets.config import Config

c = get_config()  # noqa: F821

# ------------------------ #
# Sandboxed autograding    #
# ------------------------ #
# Swap Execute for SandboxedExecute in the autograde pipeline only. Validate also
# runs Execute, but outside /autograded/, where the sandbox refuses to start.
# c.Execute.kernel_manager_class would not work: nbgrader's Execute passes the
# kernel manager as a constructor kwarg, which overrides config.
EXECUTE = "nbgrader.preprocessors.Execute"
SANDBOXED_EXECUTE = "autograde_sandbox.SandboxedExecute"

e2xgrader_config = Config()
configure_base(e2xgrader_config)
autograde_preprocessors = list(e2xgrader_config.Autograde.autograde_preprocessors)
if EXECUTE not in autograde_preprocessors:
    raise RuntimeError(f"{EXECUTE} not found in e2xgrader's autograde preprocessors")
c.Autograde.autograde_preprocessors = [
    SANDBOXED_EXECUTE if p == EXECUTE else p for p in autograde_preprocessors
]

# Refuse to run without signal scoping (ABI 6); all our nodes support it.
c.SandboxedKernelManager.min_abi = 6

# glibc's tmpfile() always uses /tmp, which the sandbox hides (xeus-cpp crashes on
# its first cell). This shim makes it use the kernel's private TMPDIR instead.
c.SandboxedKernelManager.ld_preload = ["/usr/local/lib/libtmpfile_tmpdir.so"]


# ------------------------ #
# Shared materials         #
# ------------------------ #
def _overlaps(path, other):
    """True if one path is the other or contains it."""
    return os.path.commonpath([path, other]) in (path, other)


def _shared_path_problem(real, home, course, exchange):
    """Why autograded code must not read this shared path, or None if it may."""
    if os.path.commonpath([real, home]) == real:
        return "is $HOME or one of its parents"
    if _overlaps(real, course):
        return "overlaps the course directory"
    if _overlaps(real, exchange):
        return "overlaps the exchange"
    # Folders in $HOME are fine (e.g. a shared volume mounted at ~/shared), hidden
    # ones are not: that is where keys and runtime files live (.ssh, .local, ...).
    if os.path.commonpath([real, home]) == home and any(
            part.startswith(".") for part in os.path.relpath(real, home).split(os.sep)):
        return "is a hidden folder in $HOME"
    return None


def _safe_shared_paths():
    home = os.path.realpath(os.path.expanduser("~"))
    course = os.path.realpath(os.path.expanduser(os.getenv("NBGRADER_COURSE_DIR") or os.getcwd()))
    exchange = os.path.realpath(os.getenv("NBGRADER_EXCHANGE_DIR", "/srv/nbgrader/exchange"))
    safe = []
    for path in os.getenv("E2X_SHARED_PATHS", "").split(os.pathsep):
        if not path:
            continue
        real = os.path.realpath(os.path.expanduser(path))
        problem = _shared_path_problem(real, home, course, exchange)
        if problem:
            sys.stderr.write(f"[autograde-sandbox] not exposing shared path {path!r}: {problem}\n")
            continue
        safe.append(real)
    return safe


c.SandboxedKernelManager.extra_read_paths = _safe_shared_paths()
