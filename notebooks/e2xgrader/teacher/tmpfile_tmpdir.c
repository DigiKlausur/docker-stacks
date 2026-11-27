/*
 * tmpfile() that honors $TMPDIR, preloaded into autograde sandbox kernels
 * (LD_PRELOAD, set by autograde_sandbox.py).
 *
 * glibc's tmpfile() always creates its file in /tmp and ignores TMPDIR. The
 * sandbox hides /tmp, so tmpfile() fails there, and xeus-cpp (CppInterOp's
 * output capture) crashes on its first cell. This version creates the same
 * kind of unnamed temporary file in $TMPDIR, the kernel's private directory.
 *
 * Build: gcc -shared -fPIC -O2 -o libtmpfile_tmpdir.so tmpfile_tmpdir.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

FILE *tmpfile(void)
{
    const char *dir = getenv("TMPDIR");
    char path[4096];
    int fd;
    FILE *file;

    if (dir == NULL || *dir == '\0')
        dir = "/tmp";
    if (snprintf(path, sizeof path, "%s/tmpfXXXXXX", dir) >= (int)sizeof path)
        return NULL;
    fd = mkstemp(path);
    if (fd < 0)
        return NULL;
    unlink(path);
    file = fdopen(fd, "w+");
    if (file == NULL)
        close(fd);
    return file;
}

FILE *tmpfile64(void)
{
    return tmpfile();
}
