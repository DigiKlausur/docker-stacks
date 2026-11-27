"""
nbgrader configuration for the teacher image: autograding runs in the Landlock
sandbox (autograde_sandbox.py). Installed to /opt/conda/etc/jupyter, so it loads
after /etc/jupyter/nbgrader_config.py (shared by all modes) and takes precedence.
A course's own nbgrader_config.py still loads last and could undo this.

This uses the environment variables:
- E2X_SHARED_PATHS: Colon-separated directories with shared materials. Autograded
  code may read them. Paths overlapping $HOME, the course directory or the
  exchange are skipped, so the sandbox never exposes them.
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
    return path == other or path.startswith(other + os.sep) or other.startswith(path + os.sep)


def _safe_shared_paths():
    home = os.path.realpath(os.path.expanduser("~"))
    course = os.path.realpath(os.path.expanduser(os.getenv("NBGRADER_COURSE_DIR") or os.getcwd()))
    exchange = os.path.realpath(os.getenv("NBGRADER_EXCHANGE_DIR", "/srv/nbgrader/exchange"))
    safe = []
    for path in os.getenv("E2X_SHARED_PATHS", "").split(os.pathsep):
        if not path:
            continue
        real = os.path.realpath(os.path.expanduser(path))
        if real == "/" or home.startswith(real + os.sep) or real == home \
                or _overlaps(real, course) or _overlaps(real, exchange):
            sys.stderr.write(f"[autograde-sandbox] not exposing shared path {path!r}: "
                             "overlaps $HOME, the course directory or the exchange\n")
            continue
        safe.append(real)
    return safe


c.SandboxedKernelManager.extra_read_paths = _safe_shared_paths()
