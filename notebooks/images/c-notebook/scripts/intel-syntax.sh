alias objdump='objdump -M intel'

# clang/gcc haben keinen globalen Intel-Schalter; -masm=intel pro Aufruf.
# Workaround: Intel-Assembly aus einer C-Datei erzeugen.
#   cintel datei.c   ->  datei.s (Intel-Syntax, -O0)
cintel() {
    [ -n "$1" ] || { echo "usage: cintel <datei.c> [clang-flags...]"; return 1; }
    local src="$1"; shift
    "${CC:-clang}" -S -masm=intel -O0 -fno-asynchronous-unwind-tables "$@" "$src" -o "${src%.c}.s"
}