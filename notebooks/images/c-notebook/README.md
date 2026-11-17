# e2x C Notebook

This Docker image is a customized version of the [e2x Minimal Notebook](../minimal-notebook) image, with kernels for C and C++.

## Description

The image offers two kinds of kernels, so a course can pick the one that fits:

* **C** ([jupyter-c-kernel](https://github.com/brendan-rius/jupyter-c-kernel)): C11, compiled with gcc. Each cell is compiled and run as its own program, so cells share no state: a cell that calls a function must also define it.
* **C11 / C17 / C23** and **C++17 / C++20 / C++23**, each C23/C++23 also with OpenMP ([xeus-cpp](https://github.com/compiler-research/xeus-cpp)): interpreters based on clang-repl. Cells share state like in Python, so later cells (e.g. autograder tests) can call functions from earlier ones.

In the kernel menu, "C" is the gcc kernel and "C11", "C17", "C23" are the interpreted ones.

`build-essential` (gcc, make) is installed, so C programs can also be compiled in the terminal.

## Usage

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.
