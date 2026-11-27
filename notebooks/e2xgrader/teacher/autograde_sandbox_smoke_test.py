#!/usr/bin/env python3
"""
Smoke test for the autograde sandbox: runs every installed kernel through
autograde_sandbox.SandboxedExecute (the preprocessor nbgrader autograde uses in
the teacher image), with the nbgrader config nbgrader itself would load here,
in a fake course and checks that it cannot escape.

Usage (inside a teacher image):  autograde-sandbox-smoke-test

Per kernel, a probe tries to read its own data.csv (must work), append to the
gradebook and to another student's folder (must fail) and read
JUPYTERHUB_API_TOKEN (must be unset); the Python probe also tries to read its
parent's /proc/<pid>/environ (must fail). Kernels without a probe (e.g.
java_syntax_kernel, which does not run code) only have to start in the sandbox.
Julia kernels are skipped. Afterwards, every file outside the student's own
folder must be unchanged, and a kernel started outside /autograded/ must be
refused.

Exit codes: 0 all passed, or Landlock unavailable (reported, nothing tested);
1 a check failed.
"""
import hashlib
import os
import subprocess
import sys
import tempfile

import autograde_sandbox
import nbformat
from autograde_sandbox import SandboxedExecute
from e2xcore.utils.utils import get_nbgrader_config
from jupyter_client.kernelspec import KernelSpecManager

SECRET = "smoke-test-secret"
DATA = "alice-data"

# Any readable parent environment fails: /proc/<pid>/environ only shows a process'
# initial environment, so the test's own SECRET (set later) would not show up in it
# even when the grader's real credentials would.
PYTHON_PROBE = """\
import os
print("READ", open("data.csv").read().strip())
for name, path in [("GRADEBOOK", "../../../gradebook.db"), ("BOB", "../../bob/pwned")]:
    try:
        open(path, "a").close()
        print(name, "WRITABLE")
    except OSError:
        print(name, "BLOCKED")
print("TOKEN", os.environ.get("JUPYTERHUB_API_TOKEN", "UNSET"))
try:
    with open(f"/proc/{os.getppid()}/environ", "rb") as f:
        f.read()
    print("PARENT_ENV READABLE")
except OSError:
    print("PARENT_ENV BLOCKED")
"""

# Valid C and C++: used by the gcc C kernel (as a program) and by xeus-cpp.
C_PROBE = r"""
#include <stdio.h>
#include <stdlib.h>

static int probe(void) {
    char line[64] = "";
    FILE *in = fopen("data.csv", "r");
    if (in) { fgets(line, sizeof line, in); fclose(in); }
    printf("READ %s\n", line);
    const char *names[] = {"GRADEBOOK", "BOB"};
    const char *paths[] = {"../../../gradebook.db", "../../bob/pwned"};
    for (int i = 0; i < 2; i++) {
        FILE *out = fopen(paths[i], "a");
        printf("%s %s\n", names[i], out ? "WRITABLE" : "BLOCKED");
        if (out) fclose(out);
    }
    const char *token = getenv("JUPYTERHUB_API_TOKEN");
    printf("TOKEN %s\n", token ? token : "UNSET");
    fflush(stdout);
    return 0;
}
"""

EXPECTED = [f"READ {DATA}", "GRADEBOOK BLOCKED", "BOB BLOCKED", "TOKEN UNSET"]


def probe_cells(spec):
    """Cells to run for a kernelspec; None = start-only check."""
    argv = " ".join(spec.argv)
    if "java_syntax_kernel" in argv:
        return None
    if spec.language.lower() == "python":
        return [PYTHON_PROBE]
    if "jupyter_c_kernel" in argv:  # each cell is compiled and run as a program
        return [C_PROBE + "\nint main(void) { return probe(); }\n"]
    if os.path.basename(spec.argv[0]) == "xcpp":  # clang-repl: cells share state
        return [C_PROBE, "probe();"]
    return None


def make_course(root):
    alice = os.path.join(root, "autograded", "alice", "ps1")
    bob = os.path.join(root, "autograded", "bob", "ps1")
    os.makedirs(alice)
    os.makedirs(bob)
    for path, content in [(os.path.join(root, "gradebook.db"), "grades"),
                          (os.path.join(alice, "data.csv"), DATA),
                          (os.path.join(bob, "answers.txt"), "bob's answers")]:
        with open(path, "w") as f:
            f.write(content)
    return alice


def snapshot(root, writable):
    """Hashes of all files under root, except in the writable folder."""
    files = {}
    for dirpath, _, filenames in os.walk(root):
        if dirpath.startswith(writable):
            continue
        for name in filenames:
            path = os.path.join(dirpath, name)
            with open(path, "rb") as f:
                files[os.path.relpath(path, root)] = hashlib.sha256(f.read()).hexdigest()
    return files


def run(config, kernel_name, language, cells, cwd):
    """Execute the cells with SandboxedExecute in cwd; return all stream output."""
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(c) for c in cells])
    nb.metadata.kernelspec = {"name": kernel_name, "display_name": kernel_name,
                              "language": language}
    executor = SandboxedExecute(config=config, timeout=120)
    nb, _ = executor.preprocess(nb, {"metadata": {"path": cwd}})
    return "".join(out.get("text", "") for cell in nb.cells for out in cell.get("outputs", []))


def check_kernel(config, name, spec, course, alice, before):
    cells = probe_cells(spec)
    try:
        output = run(config, name, spec.language, cells or [""], alice)
    except Exception as e:
        return [f"kernel failed to run: {type(e).__name__}: {e}"]
    problems = []
    if cells is not None:
        problems += [f"missing {line!r} in output" for line in EXPECTED if line not in output]
        if "WRITABLE" in output or "READABLE" in output or SECRET in output:
            problems.append("sandbox escape reported in output")
    if snapshot(course, alice) != before:
        problems.append("files outside the student's folder changed")
    if problems:
        problems.append(f"output was:\n{output}")
    return problems


def main():
    check = subprocess.run([sys.executable, "-I", autograde_sandbox.__file__, "--check"],
                           capture_output=True, text=True)
    print(check.stdout, end="")
    if check.returncode != 0:
        print("Landlock unavailable: sandbox not tested")
        return 0

    # nbgrader's own config loading, including a course's or the cwd's nbgrader_config.py
    config = get_nbgrader_config()
    print(f"SandboxedKernelManager config: {dict(config.SandboxedKernelManager)}")

    os.environ["JUPYTERHUB_API_TOKEN"] = SECRET
    failed = False
    with tempfile.TemporaryDirectory(prefix="sandbox-smoke-") as tmp:
        course = os.path.join(tmp, "course")
        alice = make_course(course)
        before = snapshot(course, alice)

        ksm = KernelSpecManager()
        names = []
        for name in sorted(ksm.find_kernel_specs()):
            if name.startswith("julia"):
                print(f"SKIP {name} (Julia is not tested)")
            else:
                names.append(name)
        if not names:
            print("FAIL no kernels to test")
            return 1

        for name in names:
            spec = ksm.get_kernel_spec(name)
            kind = "probe" if probe_cells(spec) is not None else "start only"
            problems = check_kernel(config, name, spec, course, alice, before)
            print(f"{'FAIL' if problems else 'PASS'} {name} ({kind})")
            for problem in problems:
                print(f"    {problem}")
            failed |= bool(problems)

        # Outside /autograded/, the sandbox must refuse to start any kernel.
        try:
            run(config, names[0], ksm.get_kernel_spec(names[0]).language, [""], course)
            print("FAIL kernel started outside /autograded/")
            failed = True
        except Exception:
            print("PASS kernel refused outside /autograded/")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
