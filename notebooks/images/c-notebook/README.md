# e2x C Notebook

This Docker image is a customized version of the [e2x Minimal Notebook](../minimal-notebook) image for systems programming: kernels for C and C++, the usual C toolchain and debugging tools, and VS Code.

## Description

The image offers two kinds of kernels, so a course can pick the one that fits:

* **C** ([jupyter-c-kernel](https://github.com/brendan-rius/jupyter-c-kernel)): C11, compiled with gcc. Each cell is compiled and run as its own program, so cells share no state: a cell that calls a function must also define it.
* **C11 / C17 / C23** and **C++17 / C++20 / C++23**, each C23/C++23 also with OpenMP ([xeus-cpp](https://github.com/compiler-research/xeus-cpp)): interpreters based on clang-repl. Cells share state like in Python, so later cells (e.g. autograder tests) can call functions from earlier ones.

In the kernel menu, "C" is the gcc kernel and "C11", "C17", "C23" are the interpreted ones.

## Tools

* **Build:** gcc, clang, make, cmake, meson, ninja, autotools, pkg-config, bear
* **Debug and analyze:** gdb, lldb, valgrind, strace, ltrace, elfutils, libtree,
  sanitizers (`-fsanitize=address,undefined,thread`), cppcheck, clang-tidy, clang-format
* **Misc:** xxd, hexdump, netcat, GNU parallel, btop
* **Man pages** for the C library and system calls (`man 3 printf`, `man 2 write`).
  The base image is minimized and drops man pages; this image restores them for
  everything it installs.
* **Intel assembly syntax by default:** `objdump` is an alias for `objdump -M intel`,
  `cintel file.c` writes `file.s` in Intel syntax, and gdb disassembles in Intel syntax
  ([scripts/intel-syntax.sh](scripts/intel-syntax.sh), `/etc/gdb/gdbinit.d/e2x.gdb`).
  gdb keeps ASLR on, because containers do not allow turning it off.
* **Java 25 JDK** (Eclipse Temurin), e.g. for calling C from Java via the Foreign
  Function & Memory API (`java --enable-native-access=ALL-UNNAMED ...`).
* **VS Code** (code-server) opens from the launcher or "New → VS Code".

## Usage

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.
