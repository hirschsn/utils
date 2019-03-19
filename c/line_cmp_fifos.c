/* MIT/Expat license
 *
 * Copyright 2018 Steffen Hirschmann
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int rflag = 0;

void print_state(const char *filename, int closed_flag, char *contents)
{
    printf("%s:", filename);
    if (closed_flag)
        printf(" pipe closed.\n");
    else
        printf("\n%s\n", contents);
}

/** Returns 1 if pipe has been closed, else 0.
 *  If rflag is true, always returns 0.
 */
int read_pipe(FILE **p, char *buffer, size_t nelem, const char *filename)
{
    if (rflag) {
        while (fgets(buffer, nelem, *p) == NULL) {
            fclose(*p);
            *p = fopen(filename, "r");
        }
        return 0;
    } else {
        return fgets(buffer, nelem, *p) == NULL;
    }
}

_Noreturn void eusage(const char *argv0)
{
    fprintf(stderr, "Usage: %s [-r] FILE1 FILE2\n", argv0);
    exit(1);
}

int main(int argc, char *argv[])
{
    int ret = 0, pipe_end1, pipe_end2;
    FILE *f1, *f2;
    char s1[BUFSIZ], s2[BUFSIZ];
    size_t lineno;

    if (argc < 3 || argc > 4)
        eusage(*argv);

    if (argc == 4) {
        if (strcmp(argv[1], "-r") == 0) {
            rflag = 1;
            puts("Reopen mode.");
            argv++;
            argc--;
        } else {
            eusage(*argv);
        }
    }

    if (!(f1 = fopen(argv[1], "r"))) {
        perror("fopen:");
        exit(1);
    }
    if (!(f2 = fopen(argv[2], "r"))) {
        perror("fopen:");
        fclose(f1);
        exit(1);
    }

    for (lineno = 1;; lineno++) {
        pipe_end1 = read_pipe(&f1, s1, BUFSIZ, argv[1]);
        pipe_end2 = read_pipe(&f2, s2, BUFSIZ, argv[2]);

        if (strcmp(s1, s2) != 0 || pipe_end1 != pipe_end2) {
            fprintf(stderr, "Difference in line %zu.\n", lineno);
            print_state(argv[1], pipe_end1, s1);
            print_state(argv[2], pipe_end2, s2);
            ret = 255;
            break;
        }

        if (pipe_end1 && pipe_end2)
            break;
    }

    fclose(f1);
    fclose(f2);
    return ret;
}

