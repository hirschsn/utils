#!/usr/bin/python3
"""
Prints stats about the kinetic energy of a binary snapshot of 3d velocities.
The snapshots must be IEEE-754 doubles and compatible with this machine.
"""

import sys
import numpy as np


def load_vel_field(fn):
    a = np.fromfile(fn)
    if a.shape[0] % 3 != 0:
        raise RuntimeError("Shape of {} not a multiple of 3.".format(fn))
    return a.reshape(a.shape[0] // 3, 3)


def energy_stats(vel):
    vmag = np.linalg.norm(vel, axis=1)
    ekin = .5 * vmag**2
    return np.max(ekin), np.average(ekin), np.min(ekin)


def print_header():
    print("{:25s} {:10s} {:10s} {:10s}".format(
        "File", "Max E_kin", "Avg E_kin", "Min E_kin"))


def print_stats(fn):
    vel = load_vel_field(fn)
    emax, eavg, emin = energy_stats(vel)
    print("{:25s} {:10f} {:20f} {:10f} (shape: {}x{})".format(
        fn, emax, eavg, emin, vel.shape[0], vel.shape[1]))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print_header()
    for fn in sys.argv[1:]:
        print_stats(fn)
    print()
