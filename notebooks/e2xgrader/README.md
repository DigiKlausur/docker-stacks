# E2xGrader Notebook

This Docker image is used to install `e2xgrader` and activate a specific mode.   
More information on e2xgrader can be found [here](https://github.com/Digiklausur/e2xgrader).

## Build Args

The following build args are available:

* `E2XGRADER_VERSION`: The e2xgrader version to install from PyPI. Pinned by its default in the [Dockerfile](Dockerfile); bump it there to update all e2x images. An empty value installs the latest version. Has no effect if `FROM_REPO` is `true`.
* `FROM_REPO`: If e2xgrader should be installed from the [GitHub repository](https://github.com/Digiklausur/e2xgrader). Defaults to `false`.
* `E2XGRADER_BRANCH`: Specifies the branch to install from if `FROM_REPO` is `true`. Defaults to `main`.

## Build Targets

This image uses multistage builds with the following available targets:

* `base`: Base configuration with common requirements for all modes
* `student`: Student mode configuration
* `student_exam`: Student exam mode configuration with restricted environment
* `teacher`: Teacher mode configuration with grading and assignment management tools

## Description

This image is designed to build e2xgrader end-point images for the other images in this repository using multistage builds.

The `base` target installs common requirements for all modes, including:
* An `nbgrader_config.py` activating `e2xgrader` preprocessors and the `e2xgrader` exchange
* [e2xgradingtools](https://github.com/DigiKlausur/e2xgradingtools) for testing students code
* [exam_kernel](https://github.com/DigiKlausur/exam_kernel) for providing a restricted and configurable Python kernel
* [java_syntax_kernel](https://github.com/DigiKlausur/java_syntax_kernel) for providing a simple kernel that highlights JAVA code without executing it.

### Environment Variables

These images can be customized using environment variables. For all modes the following environment variables are present.

* `LANGUAGE`: The language to use (default: en). This currently only affects the submission html generated in `student_exam` mode.

* `NBGRADER_TIMEZONE`: The timezone to use (default: Europe/Berlin)

* `NBGRADER_COURSE_DIR`: The root directory for the course (default: ~/course)
* `NBGRADER_COURSE_ID`: The course id (default: course101)
* `NBGRADER_GROUPSHARED`: Whether the course directory is group-shared (default: true)

* `NBGRADER_EXCHANGE_DIR`: The exchange directory (default: /srv/nbgrader/exchange)
* `NBGRADER_EXCHANGE_PERSONALIZED_INBOUND`: Whether to use personalized inbound exchange. If active students submit to their own directory.
* `NBGRADER_EXCHANGE_PERSONALIZED_OUTBOUND`: Whether to use personalized outbound exchange. If active students fetch from their own directory. This can be used to provide each student with a personalized assignment.
* `NBGRADER_EXCHANGE_PERSONALIZED_FEEDBACK`: Whether to use personalized feedback exchange. If active students fetch feedback from their own directory.

* `NBGRADER_EXECUTE_TIMEOUT`: The timeout for executing notebooks in seconds (default: 300)

* `E2X_DRAWIO_DOMAIN`: The domain to use for the diagram editor (default: None). If None is set then `https://embed.diagrams.net/` is used.
* `E2X_DRAWIO_ORIGIN`: The origin to use for the diagram editor (default: None). If None is set then `https://embed.diagrams.net/` is used.

* `E2X_SHARED_PATHS`: Colon-separated directories with shared materials, like `PATH` (default: None). In teacher mode, autograded code may read them, except `$HOME` itself and its parents, hidden folders in `$HOME` (`.ssh`, `.local`, …) and paths overlapping the exchange, which are skipped. If a shared path overlaps the course being graded, autograding refuses to start (see [Sandboxed Autograding](#sandboxed-autograding)). Folders in `$HOME`, such as a shared volume mounted at `~/shared`, are fine.

### Teacher Target

The `teacher` target builds from the `base` stage and:

* Installs wkhtml2pdf and [pdf_feedback_exporter](https://github.com/DigiKlausur/e2xgradingtools) for generating PDF versions of student feedback files
* Installs RISE for Jupyter Notebook slide shows
* Installs [e2x_exam_sheets](https://github.com/DigiKlausur/e2xgradingtools) for generating seating cards and login sheets for exams
* Runs autograding in a Landlock sandbox (see [Sandboxed Autograding](#sandboxed-autograding))
* Activates e2xgrader in teacher mode

### Student Target

The `student` target builds from the `base` stage and:

* Installs RISE for Jupyter Notebook slide shows
* Activates e2xgrader in student mode with student extensions

### Student Exam Target

The `student_exam` target builds from the `base` stage and:

* Activates student exam extensions, providing a restricted notebook environment
* Activates a custom submit toolbar in notebooks
* Activates custom submit behavior that hashes student files on submission and provides HTML versions of all submitted notebooks
* Activates e2xgrader in student_exam mode

In student exam mode the following additional environment variables can be used to configure automated backups using [E2X Jupyter Backup](https://github.com/DigiKlausur/e2x-jupyter-backup).

* `E2X_BACKUP_ENABLED`: Whether the backup functionality is enabled (default: false)
* `E2X_BACKUP_DIR`: The directory where backups are stored. Either relative or absolute, see [E2X Jupyter Backup](https://github.com/DigiKlausur/e2x-jupyter-backup) for details.
* `E2X_BACKUP_MAX_FILES`: The maximum number of backup files to keep per notebook (default: 10)
* `E2X_BACKUP_MAX_SIZE_MB`: The maximum size of backup files in megabytes
* `E2X_MIN_SECONDS_BETWEEN_BACKUPS`: The minimum number of seconds between backups for the same notebook

## Sandboxed Autograding

In `teacher` images, autograding runs every student notebook in a sandbox, from the formgrader as well as with `nbgrader autograde`. Without it, student code runs as the grader, with access to the course directory, the gradebook, every other submission and the grader's JupyterHub token.

The sandbox uses [Landlock](https://docs.kernel.org/userspace-api/landlock.html), a Linux security module that needs no root, capabilities or user namespaces, so it works in a normal JupyterHub pod. It wraps whatever kernel a notebook uses, so it works for every kernel without changing kernelspecs. The code is in [teacher/autograde_sandbox.py](teacher/autograde_sandbox.py).

What autograded code can do:

| | Allowed | Blocked |
|---|---|---|
| Files | Read system paths (`/usr`, `/opt`, `/etc`, …) and `E2X_SHARED_PATHS`. Write its own `autograded/<student>/<assignment>` folder, a private temp directory and `/dev/shm`. | Everything under `/home` (course directory, gradebook, other submissions), `/tmp`, `/srv` (exchange), `/root`, `/run`, `/mnt`, `/media`. Other processes' `/proc` entries. |
| Permissions | `chmod` its own files, without group/other write or setuid/setgid/sticky bits. New files get `umask 022`. | Making any file group- or world-writable or setuid, `chown`, setting or removing xattrs (ACLs). Landlock cannot restrict these, so a seccomp filter blocks them. |
| Network | Its kernel's own ports | All other TCP, binding and connecting |
| Processes | Its own child processes | Signals to processes outside the sandbox. Gaining privileges (`sudo`, setuid binaries). |
| Environment | | Hub tokens and other secrets (`JUPYTERHUB_*`, names containing `TOKEN`, `SECRET`, `PASSWORD`, …) are removed. |

The sandbox fails closed: the kernel does not start and autograding reports "Kernel died" if
* Landlock is unavailable or older than ABI 6 (Linux 6.12), or the seccomp filter cannot be installed (it exists for x86_64 only),
* a notebook does not run inside an `/autograded/` folder, or
* the course directory would be readable, because a shared path or a system directory contains it or lies inside it. The course directory is the part of the notebook's folder before `/autograded/`, so this also catches a course outside the hidden top-level directories.

It never falls back to running unsandboxed.

### Checking It

* Landlock support of the node, inside a teacher container:
  ```bash
  python -I "$(python -c 'import autograde_sandbox; print(autograde_sandbox.__file__)')" --check
  ```
* The whole setup with every installed kernel (results on stdout, kernel output on stderr; exits 1 if a check fails):
  ```bash
  autograde-sandbox-smoke-test 2>/dev/null
  ```
* During autograding, every kernel start logs a line like this to the output of `nbgrader autograde` or the grader's server log. If it is missing, autograding is not sandboxed.
  ```
  [autograde-sandbox] Landlock ABI 6 active (fs=True, net=True, signals=True, perms=True); writable: …/autograded/<student>/<assignment>; kernel: /opt/conda/bin/python3
  ```

### Configuration

The teacher image installs [teacher/nbgrader_config.py](teacher/nbgrader_config.py) to `/opt/conda/etc/jupyter/`. It replaces nbgrader's `Execute` preprocessor with `autograde_sandbox.SandboxedExecute` in the autograde pipeline only. (`c.Execute.kernel_manager_class` does not work: nbgrader's `Execute` overrides it.) The build fails if nbgrader's merged config does not contain the sandboxed pipeline.

Settings of `SandboxedKernelManager`:

| Setting | Default | Teacher image |
|---|---|---|
| `min_abi` | `1` | `6`: requires signal scoping |
| `extra_read_paths` | `[]` | `E2X_SHARED_PATHS`, without `$HOME` and its parents, hidden folders in `$HOME` and paths overlapping the exchange |
| `ld_preload` | `[]` | `/usr/local/lib/libtmpfile_tmpdir.so`: makes `tmpfile()` use the private temp directory, because glibc's always uses the hidden `/tmp` ([teacher/tmpfile_tmpdir.c](teacher/tmpfile_tmpdir.c); xeus-cpp needs it) |
| `deny_top` | `home:root:run:tmp:srv:mnt:media` | default |
| `cwd_must_contain` | `/autograded/` | default |
| `allow_network` | `False` | default |

Never add the course directory, `$HOME` or the exchange to `extra_read_paths`.

### Limitations

* A course's own `nbgrader_config.py` loads last. If it sets `c.Autograde.autograde_preprocessors`, it replaces the sandboxed pipeline.
* Kernels must be installed system-wide. Kernelspecs or environments under `/home` cannot start in the sandbox, including kernelspecs in `~/.local/share/jupyter/kernels` of a persistent home, which take precedence over the image's.
* Permissions can still be *removed* from files the grader owns: `chmod 0` or `chmod 444` on the gradebook stops grading until the permissions are fixed. The seccomp filter only blocks making files more accessible, because blocking removal would break normal code: nbgrader makes autograded files `0444`, and copies keep that mode. Timestamps (`touch`, `utime`) are not restricted either.
* Not covered: UDP, CPU and memory use (only `NBGRADER_EXECUTE_TIMEOUT` limits a run), students faking their own test results, and student HTML/JavaScript output rendered in the formgrader.
* Validating (`nbgrader validate`, the Validate button) is not sandboxed: it runs outside `/autograded/`.
* ipykernel cannot bind its IOPub pipe, so output of forked child processes is not captured. It also logs a harmless traceback at shutdown, because it cannot list processes in `/proc`.
* Every run leaves a small `/tmp/autograde-sandbox-*` directory behind.
* Secrets are removed from the environment by name (a denylist). Add the names of any other secrets you put into the environment to `DROP_ENV_PREFIXES` / `DROP_ENV_SUBSTRINGS` in [teacher/autograde_sandbox.py](teacher/autograde_sandbox.py).
* Julia kernels are not tested.

## Usage

This image isn't used on its own: every image marked `[e2x]` gets one variant per target.
See [E2xGrader Images](../../README.md#e2xgrader-images) and
[Building Locally](../../README.md#building-locally) in the main README.

### Running the Images

After building an image, you can run it with customized environment variables. Here are some examples:

**Basic run with default settings:**

```bash
docker run -p 8888:8888 your-notebook-student:dev
```

**Run with custom course configuration:**

```bash
docker run -p 8888:8888 \
  -e NBGRADER_COURSE_ID="intro_to_python" \
  -e NBGRADER_TIMEZONE="America/New_York" \
  -v /path/to/exchange:/srv/nbgrader/exchange \
  your-notebook-teacher:dev
```

**Run student exam mode with backup enabled:**

```bash
docker run -p 8888:8888 \
  -e NBGRADER_COURSE_ID="midterm_exam" \
  -e E2X_BACKUP_ENABLED="true" \
  -e E2X_BACKUP_MAX_FILES="20" \
  -v /path/to/exchange:/srv/nbgrader/exchange \
  your-notebook-student-exam:dev
```
