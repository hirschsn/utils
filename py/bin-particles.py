#!/usr/bin/python3
#
# Read particles, fold and bin them to a grid.
# Copyright 2019, Steffen Hirschmann
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import sys
import math
import numpy as np

if len(sys.argv) != 5:
    print("Usage: {} POS-FILE BOX NCELLS RESULT-FILE".format(sys.argv[0]), file=sys.stderr)
    print("Example: {} positions.bin 800.0,800.0,800.0 128,128,128 lcgrid.npy".format(sys.argv[0]), file=sys.stderr)
    raise SystemExit(1)

if sys.argv[1].endswith(".npy"):
    print("Loading npy")
    pos = np.load(sys.argv[1])
    print("Loading txt")
elif sys.argv[1].endswith(".txt"):
    pos = np.loadtxt(sys.argv[1])
else:
    print("Loading binary dump")
    pos = np.fromfile(sys.argv[1])
    assert pos.shape[0] % 3 == 0
    pos.resize((pos.shape[0] // 3, 3))

assert len(pos.shape) == 2 and pos.shape[1] == 3

print("Read: {} particles".format(pos.shape[0]))

box = np.array([float(b) for b in sys.argv[2].split(",")])
lcgrid = np.array([int(g) for g in sys.argv[3].split(",")], dtype=int)
cellsize = np.array([b / g for b, g in zip(box, lcgrid)])

print("Box      :", box)
print("Ncells   :", lcgrid)
print("Cell size:", cellsize)

pos -= np.floor(pos / box) * box
assert np.all(pos >= 0.) and np.all(pos < box)

# Bin particles to linked cells
rng = [(0, b) for b in box]
g = np.histogramdd(pos, bins=lcgrid, range=rng)

np.save(sys.argv[4], g[0])
print("Wrote lc grid of shape {} to {}.".format(g[0].shape, sys.argv[4]))

