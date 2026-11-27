#!/usr/bin/env python3
"""
autograde_sandbox - run ANY Jupyter kernel confined by Linux Landlock.

Kernel-agnostic: instead of a special kernelspec, nbclient is given a
KernelManager that prefixes whatever command the notebook's kernelspec would
run (python, java, xcpp, R, bash, ...) with this module as a wrapper. The
wrapper locks itself down with Landlock and then exec()s the real kernel, so
the kernel and every process it spawns:

  * may read/execute system paths (/usr, /opt, /etc, /lib, ...) but NOT
    /home, /root, /run, /tmp, /srv, /mnt, /media   (deny_top)
    and of /proc only its own /proc/<pid> plus global info files (cpuinfo, ...)
  * may write ONLY to its working directory (the student's autograded folder),
    a private temp dir and /dev/shm (+ open /dev/null, ptys, ...)
  * cannot open or bind TCP sockets other than its own kernel ports
                                                (Landlock ABI >= 4, Linux >= 6.7)
  * cannot ptrace / signal processes outside the sandbox
                                       (signals: Landlock ABI >= 6, Linux >= 6.12)
  * cannot gain privileges (no_new_privs: sudo / setuid binaries are inert)
  * gets an environment without hub tokens / credentials

Fail closed: if Landlock is unavailable, the working directory looks wrong, the
course directory (the part of the working directory before /autograded/) would
be readable, or the kernel would be started by a non-local provisioner, starting
the kernel fails, so autograding errors out instead of running unsandboxed.

Usage with nbgrader / e2xgrader (module must be importable by the grader):

    # nbgrader_config.py: replace nbgrader's Execute in the autograde pipeline only
    # (validate also runs Execute, outside /autograded/, and must stay unsandboxed).
    # c.Execute.kernel_manager_class does NOT work: nbgrader's Execute passes
    # kernel_manager_class as a constructor kwarg, which overrides config.
    c.Autograde.autograde_preprocessors = [
        "autograde_sandbox.SandboxedExecute" if p == "nbgrader.preprocessors.Execute" else p
        for p in AUTOGRADE_PREPROCESSORS  # e.g. from e2xgrader.config.configure_base
    ]
    # optional:
    # c.SandboxedKernelManager.extra_read_paths = ["/srv/datasets"]
    # c.SandboxedKernelManager.cwd_must_contain = "/autograded/"
    # c.SandboxedKernelManager.allow_network = False
    # c.SandboxedKernelManager.ld_preload = ["/usr/local/lib/libtmpfile_tmpdir.so"]

Check host support:   python autograde_sandbox.py --check
Wrapper (normally invoked by SandboxedKernelManager):
    python -I /path/to/autograde_sandbox.py --connection-file F [--extra-read P]...
        [--deny-top a:b:c] [--cwd-must-contain S] [--allow-network] [--preload LIB]...
        -- KERNEL ARGV...
"""
import ctypes
import errno
import json
import os
import shutil
import sys
import tempfile

# ---- Landlock UAPI (include/uapi/linux/landlock.h) --------------------------
SYS_LANDLOCK_CREATE_RULESET = 444  # identical on all architectures
SYS_LANDLOCK_ADD_RULE = 445
SYS_LANDLOCK_RESTRICT_SELF = 446
LANDLOCK_CREATE_RULESET_VERSION = 1 << 0
LANDLOCK_RULE_PATH_BENEATH = 1
LANDLOCK_RULE_NET_PORT = 2
PR_SET_NO_NEW_PRIVS = 38

FS_EXECUTE = 1 << 0
FS_WRITE_FILE = 1 << 1
FS_READ_FILE = 1 << 2
FS_READ_DIR = 1 << 3
FS_ABI1_ALL = (1 << 13) - 1  # EXECUTE .. MAKE_SYM
FS_REFER = 1 << 13  # ABI 2
FS_TRUNCATE = 1 << 14  # ABI 3
NET_BIND_TCP = 1 << 0  # ABI 4
NET_CONNECT_TCP = 1 << 1
SCOPE_ABSTRACT_UNIX_SOCKET = 1 << 0  # ABI 6
SCOPE_SIGNAL = 1 << 1

FS_READ = FS_EXECUTE | FS_READ_FILE | FS_READ_DIR
FS_FILE_RIGHTS = FS_EXECUTE | FS_WRITE_FILE | FS_READ_FILE | FS_TRUNCATE

DENY_TOP_DEFAULT = "home:root:run:tmp:srv:mnt:media"
# /proc/self is resolved at rule-creation time to this process' own /proc/<pid>,
# which the kernel keeps after execve.
PROC_ALLOW = [
    "/proc/self", "/proc/cpuinfo", "/proc/meminfo", "/proc/stat", "/proc/loadavg",
    "/proc/uptime", "/proc/version", "/proc/filesystems", "/proc/sys", "/proc/pressure",
]
# Env vars are dropped if their name starts with / contains one of these.
# (Denylist, because arbitrary kernels need arbitrary env: JAVA_HOME, CLASSPATH,
# R_LIBS, kernelspec "env" entries, ...)
DROP_ENV_PREFIXES = ("JUPYTERHUB_", "JPY_", "KUBERNETES_", "AWS_", "GOOGLE_", "AZURE_")
DROP_ENV_SUBSTRINGS = ("TOKEN", "SECRET", "PASSWORD", "PASSWD", "API_KEY", "ACCESS_KEY",
                       "PRIVATE_KEY", "CREDENTIAL", "COOKIE")


class RulesetAttr(ctypes.Structure):
    _fields_ = [
        ("handled_access_fs", ctypes.c_uint64),
        ("handled_access_net", ctypes.c_uint64),
        ("scoped", ctypes.c_uint64),
    ]


class PathBeneathAttr(ctypes.Structure):
    _pack_ = 1  # __attribute__((packed)) in the kernel header
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


class NetPortAttr(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("port", ctypes.c_uint64)]


_libc = ctypes.CDLL(None, use_errno=True)
_libc.syscall.restype = ctypes.c_long
_libc.prctl.restype = ctypes.c_int
L = ctypes.c_long


def _syscall(nr, *args):
    res = _libc.syscall(L(nr), *args)
    if res < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    return res


def landlock_abi():
    """Return (abi, errno). abi == 0 means Landlock is unusable."""
    try:
        return _syscall(SYS_LANDLOCK_CREATE_RULESET, None, L(0),
                        L(LANDLOCK_CREATE_RULESET_VERSION)), 0
    except OSError as e:
        return 0, e.errno


def _log(msg):
    sys.stderr.write(f"[autograde-sandbox] {msg}\n")
    sys.stderr.flush()


def _die(msg):
    _log("FATAL: " + msg)
    sys.exit(1)


def restrict(abi, read_paths, write_dirs, write_files, tcp_bind_ports, restrict_net):
    fs = FS_ABI1_ALL
    if abi >= 2:
        fs |= FS_REFER
    if abi >= 3:
        fs |= FS_TRUNCATE
    net = (NET_BIND_TCP | NET_CONNECT_TCP) if (abi >= 4 and restrict_net) else 0
    scoped = (SCOPE_ABSTRACT_UNIX_SOCKET | SCOPE_SIGNAL) if abi >= 6 else 0
    size = 24 if abi >= 6 else (16 if abi >= 4 else 8)

    attr = RulesetAttr(fs, net, scoped)
    rs = _syscall(SYS_LANDLOCK_CREATE_RULESET, ctypes.byref(attr), L(size), L(0))
    try:
        def add_path(path, access, required):
            try:
                fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
            except OSError as e:
                if required:
                    raise
                _log(f"skipping {path}: {e}")
                return
            try:
                if not os.path.isdir(path):
                    access &= FS_FILE_RIGHTS  # file rules only accept file rights
                rule = PathBeneathAttr(access & fs, fd)
                _syscall(SYS_LANDLOCK_ADD_RULE, L(rs), L(LANDLOCK_RULE_PATH_BENEATH),
                         ctypes.byref(rule), L(0))
            finally:
                os.close(fd)

        for p in read_paths:
            add_path(p, FS_READ, required=False)
        for p in write_dirs:
            add_path(p, fs, required=True)
        for p in write_files:  # device nodes / dirs of device nodes: open r/w only
            add_path(p, FS_READ_DIR | FS_READ_FILE | FS_WRITE_FILE | FS_TRUNCATE, required=False)
        if net:
            for port in tcp_bind_ports:
                rule = NetPortAttr(NET_BIND_TCP, int(port))
                _syscall(SYS_LANDLOCK_ADD_RULE, L(rs), L(LANDLOCK_RULE_NET_PORT),
                         ctypes.byref(rule), L(0))

        if _libc.prctl(ctypes.c_int(PR_SET_NO_NEW_PRIVS), ctypes.c_ulong(1),
                       ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0)) != 0:
            raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS) failed")
        _syscall(SYS_LANDLOCK_RESTRICT_SELF, L(rs), L(0))
    finally:
        os.close(rs)
    return {"fs": True, "net": bool(net), "signals": bool(scoped)}


def check():
    abi, err = landlock_abi()
    print(f"kernel release : {os.uname().release}")
    if abi < 1:
        reason = {
            errno.ENOSYS: "syscall not available: kernel < 5.13, or blocked by the seccomp profile",
            errno.EOPNOTSUPP: "Landlock compiled in but not enabled (add 'landlock' to the lsm= boot parameter)",
        }.get(err, os.strerror(err) if err else "unknown")
        print(f"Landlock       : UNAVAILABLE ({reason})")
        return 1
    print(f"Landlock ABI   : {abi}")
    print("  filesystem confinement : yes")
    print(f"  TCP bind/connect block : {'yes' if abi >= 4 else 'no (needs ABI 4 / Linux 6.7)'}")
    print(f"  signal scoping         : {'yes' if abi >= 6 else 'no (needs ABI 6 / Linux 6.12)'}")
    return 0




# ---- wrapper: lock down, then exec the real kernel ---------------------------

def _scrub_env(environ):
    return {k: v for k, v in environ.items()
            if not k.upper().startswith(DROP_ENV_PREFIXES)
            and not any(s in k.upper() for s in DROP_ENV_SUBSTRINGS)}


def overlaps(path, other):
    """True if one of the two absolute paths is the other or contains it."""
    return os.path.commonpath([path, other]) in (path, other)


def wrapper_main(argv):
    import argparse

    if "--" not in argv:
        _die("missing '--' before the kernel command")
    sep = argv.index("--")
    opts, kernel_cmd = argv[:sep], argv[sep + 1:]
    if not kernel_cmd:
        _die("empty kernel command")

    ap = argparse.ArgumentParser(prog="autograde_sandbox")
    ap.add_argument("--connection-file", required=True)
    ap.add_argument("--extra-read", action="append", default=[])
    ap.add_argument("--deny-top", default=DENY_TOP_DEFAULT)
    ap.add_argument("--cwd-must-contain", default="/autograded/")
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--min-abi", type=int, default=1)
    ap.add_argument("--preload", action="append", default=[])
    a = ap.parse_args(opts)
    for lib in a.preload:
        if not os.path.isfile(lib):
            _die(f"preload library {lib!r} not found")

    abi, err = landlock_abi()
    if abi < max(1, a.min_abi):
        _die(f"Landlock ABI {abi} < required {max(1, a.min_abi)} "
             f"({os.strerror(err) if err else 'too old'}); refusing to run unsandboxed")

    with open(a.connection_file) as f:
        conn = json.load(f)

    # --- sanity-check the working directory (this becomes writable) ---------
    cwd = os.path.realpath(os.getcwd())
    home = os.path.realpath(os.path.expanduser("~"))
    if cwd == "/" or cwd == home or home.startswith(cwd + os.sep):
        _die(f"working directory {cwd!r} is too broad")
    if a.cwd_must_contain and a.cwd_must_contain not in cwd + "/":
        _die(f"working directory {cwd!r} does not contain {a.cwd_must_contain!r}")
    # The course directory (gradebook, source/, other submissions) must stay
    # unreadable. Its root is the part of the cwd before cwd_must_contain
    # (<course>/autograded/<student>/<assignment>); the first match gives the
    # shallowest, most cautious root. Taken from the cwd rather than from config,
    # so it is the course actually being graded.
    course = None
    if a.cwd_must_contain:
        course = (cwd + "/")[:(cwd + "/").index(a.cwd_must_contain)] or "/"

    # --- private scratch space; connection file moves in there ---------------
    private = tempfile.mkdtemp(prefix="autograde-sandbox-")
    new_conn = os.path.join(private, os.path.basename(a.connection_file))
    shutil.copyfile(a.connection_file, new_conn)
    kernel_cmd = [arg.replace(a.connection_file, new_conn) for arg in kernel_cmd]
    for sub in ("tmp", "ipython", "config", "cache", "mpl"):
        os.makedirs(os.path.join(private, sub), exist_ok=True)

    env = _scrub_env(os.environ)
    env.update(
        HOME=private,
        TMPDIR=os.path.join(private, "tmp"),
        IPYTHONDIR=os.path.join(private, "ipython"),
        MPLCONFIGDIR=os.path.join(private, "mpl"),
        XDG_CONFIG_HOME=os.path.join(private, "config"),
        XDG_CACHE_HOME=os.path.join(private, "cache"),
        JUPYTER_RUNTIME_DIR=private,
        PYTHONDONTWRITEBYTECODE="1",
    )
    # JVM-based kernels ignore TMPDIR; point java.io.tmpdir at the private dir
    jto = env.get("JAVA_TOOL_OPTIONS", "")
    env["JAVA_TOOL_OPTIONS"] = (jto + f" -Djava.io.tmpdir={env['TMPDIR']} -XX:-UsePerfData").strip()
    # Preloaded libraries, e.g. a tmpfile() that honors TMPDIR (glibc's always uses
    # the hidden /tmp). Inherited by every process the kernel starts.
    preload = a.preload + ([env["LD_PRELOAD"]] if env.get("LD_PRELOAD") else [])
    if preload:
        env["LD_PRELOAD"] = ":".join(preload)

    # --- what is visible -----------------------------------------------------
    deny = set(filter(None, a.deny_top.split(":")))
    read_paths = []
    for entry in sorted(os.listdir("/")):
        if entry in deny:
            continue
        if entry == "proc":
            # NOT all of /proc: other processes' /proc/<pid>/environ would leak
            # JUPYTERHUB_API_TOKEN (e.g. of the parent grader process).
            read_paths += PROC_ALLOW
            continue
        real = os.path.realpath(os.path.join("/", entry))
        if real.strip("/").split("/")[0] in deny:  # e.g. symlink into /home
            continue
        read_paths.append(os.path.join("/", entry))
    read_paths += a.extra_read
    # A system dir or shared path containing the course, or inside it, would expose
    # it: refuse instead (e.g. a course outside the denied top-level dirs).
    if course:
        for path in read_paths:
            if overlaps(os.path.realpath(path), course):
                _die(f"read access to {path!r} would expose the course directory {course!r}")
    # the kernel executable itself may live in a denied tree (e.g. ~/.local/bin)
    write_dirs = [cwd, private] + (["/dev/shm"] if os.path.isdir("/dev/shm") else [])
    # pty support (bash/pexpect-based kernels, gdb, ...). Safe: TIOCSTI keystroke
    # injection only works on one's own controlling terminal.
    write_files = ["/dev/null", "/dev/zero", "/dev/full", "/dev/tty", "/dev/ptmx", "/dev/pts"]

    ports = []
    if conn.get("transport", "tcp") == "tcp":
        ports = [conn[k] for k in ("shell_port", "iopub_port", "stdin_port",
                                   "control_port", "hb_port") if conn.get(k)]

    try:
        active = restrict(abi, read_paths, write_dirs, write_files, ports,
                          restrict_net=not a.allow_network)
    except OSError as e:
        _die(f"applying Landlock failed: {e}")

    _log(f"Landlock ABI {abi} active (fs={active['fs']}, net={active['net']}, "
         f"signals={active['signals']}); writable: {cwd}; kernel: {kernel_cmd[0]}")
    try:
        os.execvpe(kernel_cmd[0], kernel_cmd, env)
    except OSError as e:
        _die(f"cannot exec kernel {kernel_cmd[0]!r} inside sandbox: {e} "
             "(is it installed under a denied path such as /home?)")


# ---- KernelManager for nbclient / nbgrader -----------------------------------

try:
    from jupyter_client.manager import AsyncKernelManager
    from traitlets import Bool, Integer, List, Unicode
except ImportError:  # wrapper mode only needs the stdlib
    AsyncKernelManager = None

_WRAPPER = os.path.abspath(__file__)

if AsyncKernelManager is not None:

    class SandboxedKernelManager(AsyncKernelManager):
        """Starts whatever kernel the notebook asks for, wrapped in Landlock."""

        extra_read_paths = List(Unicode(), help="Extra read-only paths (datasets, ...)").tag(config=True)
        deny_top = Unicode(DENY_TOP_DEFAULT, help="':'-separated top-level dirs to hide").tag(config=True)
        cwd_must_contain = Unicode("/autograded/", help="Refuse to start unless cwd contains this").tag(config=True)
        allow_network = Bool(False, help="Do not restrict TCP").tag(config=True)
        min_abi = Integer(1, help="Minimum Landlock ABI, e.g. 4 to require network blocking").tag(config=True)
        ld_preload = List(Unicode(), help="Libraries to preload into the kernel (LD_PRELOAD)").tag(config=True)

        def _wrapper_prefix(self):
            # Absolute path + isolated mode (-I): never "-m", which would put the
            # cwd -- the student's submission folder -- first on sys.path and let
            # a submitted autograde_sandbox.py replace the sandbox.
            cmd = [sys.executable, "-I", _WRAPPER,
                   "--connection-file", self.connection_file,
                   "--deny-top", self.deny_top,
                   "--cwd-must-contain", self.cwd_must_contain,
                   "--min-abi", str(self.min_abi)]
            for p in self.extra_read_paths:
                cmd += ["--extra-read", p]
            for lib in self.ld_preload:
                cmd += ["--preload", lib]
            if self.allow_network:
                cmd.append("--allow-network")
            return cmd + ["--"]

        def format_kernel_cmd(self, extra_arguments=None):
            return self._wrapper_prefix() + super().format_kernel_cmd(extra_arguments)

        async def _async_pre_start_kernel(self, **kw):
            kernel_cmd, kw = await super()._async_pre_start_kernel(**kw)
            # Fail closed if a non-local provisioner built the command without us.
            if kernel_cmd[:3] != [sys.executable, "-I", _WRAPPER]:
                raise RuntimeError("autograde_sandbox: kernel command is not wrapped "
                                   f"(provisioner {type(self.provisioner).__name__}); refusing to start")
            return kernel_cmd, kw

        _pre_start_kernel = _async_pre_start_kernel


# ---- nbgrader preprocessor ---------------------------------------------------
# Not needed in wrapper mode; skip there so kernel start-up does not import nbgrader.

if AsyncKernelManager is not None and __name__ != "__main__":
    try:
        from nbgrader.preprocessors import Execute
    except ImportError:  # plain nbclient use, no nbgrader installed
        Execute = None

    if Execute is not None:

        class SandboxedExecute(Execute):
            """nbgrader's Execute preprocessor, starting kernels in the sandbox.

            nbgrader's Execute.__init__ passes kernel_manager_class=AsyncKernelManager
            as a kwarg, which overrides c.Execute.kernel_manager_class from config.
            So the class is forced here instead of configured.
            """

            def __init__(self, *args, **kwargs):
                kwargs["kernel_manager_class"] = SandboxedKernelManager
                super().__init__(*args, **kwargs)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        sys.exit(check())
    sys.exit(wrapper_main(sys.argv[1:]))