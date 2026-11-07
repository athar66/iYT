// SPDX-License-Identifier: GPL-3.0-or-later
// iYT's small exec wrapper: the lock survives exec and is released on exit/crash.
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
int main(int argc, char **argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: iyt-lock LOCK PROGRAM [ARGS...]\n"); return 64; }
    const int fd = open(argv[1], O_RDWR | O_CREAT | O_NOFOLLOW, 0600);
    struct stat st;
    if (fd < 0 || fstat(fd, &st) || !S_ISREG(st.st_mode) || st.st_nlink != 1 || st.st_uid != geteuid()) {
        std::fprintf(stderr, "E_LOCK_PATH: cannot safely own service lock\n"); return 73;
    }
    if (flock(fd, LOCK_EX | LOCK_NB)) { std::fprintf(stderr, "E_ALREADY_RUNNING: iYT daemon lock is held\n"); return 75; }
    execv(argv[2], argv + 2);
    std::fprintf(stderr, "E_STARTUP: %s\n", std::strerror(errno));
    return 71;
}
