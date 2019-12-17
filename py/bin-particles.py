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

if sys.argv[1].endswith(".npy"):
    pos = np.load(sys.argv[1])
else:
    pos = np.loadtxt(sys.argv[1])

assert(len(pos.shape) == 2 and pos.shape[1] == 3)

print("Read: {} particles".format(pos.shape[0]))

box = np.array([float(b) for b in sys.argv[2].split(",")])
lcgrid = np.array([int(g) for g in sys.argv[3].split(",")], dtype=int)
cellsize = np.array([b / g for b, g in zip(box, lcgrid)])

print("Box      :", box)
print("Ncells   :", lcgrid)
print("Cell size:", cellsize)

# Fold positions to box
for i in range(3):
    col = pos[i,:]
    col[col >= box[i]] -= box[i]
    col[col < 0] += box[i]
    # 1 shift should be enough, but don't silently produce wrong results
    assert(np.all(0 <= col) and np.all(col < box[i]))

# Bin particles to linked cells
rng = [(0, b) for b in box]
g = np.histogramdd(pos, bins=lcgrid, range=rng)

np.save(sys.argv[4], g[0])
print("Wrote lc grid of shape {} to {}.".format(g[0].shape, sys.argv[4]))

