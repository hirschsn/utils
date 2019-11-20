#!/usr/bin/python3
#
# Copyright 2019 Steffen Hirschmann
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
#
# Calculate the values of alpha, beta and gamma for regular, fully-periodic,
# Cartesian grids of different sizes according to:
# Muthukrishnan et al. First- and Second-Order Diffusive Methods for Rapid,
# Coarse, Distributed Load Balancing. J. Theory Comput. Systems 31, p. 331-354
# (1998).
#

import numpy as np
from scipy import sparse
from scipy.sparse import linalg

class CLinearizer(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size

    def __call__(self, idx3d):
        return (idx3d[0] * self.grid_size[1] + idx3d[1]) * self.grid_size[2] + idx3d[2]

def fold_add(i3, j3, grid_size):
    res = np.copy(i3)
    for d in range(3):
        res[d] += j3[d]
        while res[d] < 0:
            res[d] += grid_size[d]
        while res[d] >= grid_size[d]:
            res[d] -= grid_size[d]
    return res

class NeighborGen(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
    
    def __call__(self, idx3d):
        for poffset in np.ndindex((3, 3, 3)):
            offset = poffset - np.array([1, 1, 1])
            yield fold_add(idx3d, offset, self.grid_size)


def calc_greek(gs):
    grid_size = (gs,)*3
    ncells = np.product(grid_size)

    linearize = CLinearizer(grid_size)
    neighgen = NeighborGen(grid_size)

    #M = np.zeros(shape=(ncells, ncells))
    #LC = np.zeros(shape=(ncells, ncells))
    LC = sparse.lil_matrix((ncells, ncells), dtype=np.float64)


    for idx3d in np.ndindex(grid_size):
        for jdx3d in neighgen(idx3d):
            i = linearize(idx3d)
            j = linearize(jdx3d)
            assert(i >= 0 and i < ncells)
            assert(j >= 0 and j < ncells)
            if i == j:
                LC[i, j] = 1 - 1./27.
            else:
                LC[i, j] = -1./27.
    LC = sparse.csr_matrix(LC)

    # Sanity check: doubly stochastical matrix
    #np.testing.assert_array_almost_equal(np.sum(M, axis=0), 1.0)
    #np.testing.assert_array_almost_equal(np.sum(M, axis=1), 1.0)

    #LC = np.eye(ncells, ncells) - M
    #lams = np.linalg.eigvals(LC)
    lam_2 = np.real(sparse.linalg.eigs(LC, k=2, which="SM", return_eigenvectors=False)[0])
    lam_n = np.real(sparse.linalg.eigs(LC, k=1, which="LM", return_eigenvectors=False)[0])

    ## Sanity check: Real eigenvalues
    #np.testing.assert_array_almost_equal(np.imag(lams), 0.0)

    #lams_sorted = np.sort(np.real(lams))

    ## Sanity check: \lambda_1 == 0 and all positive
    #np.testing.assert_array_almost_equal(lams_sorted[0], 0.0)

    #lam_2 = lams_sorted[1]
    #lam_n = lams_sorted[-1]

    alpha = 2 / (lam_2 + lam_n)

    gamma = (lam_n - lam_2) / (lam_n + lam_2)
    beta = 2 / (1 + np.sqrt(1 - gamma**2))

    print("Grid size:", grid_size, "Lambda_2:", lam_2, "lambda_n:", lam_n, \
        "Alpha:", alpha, "gamma:", gamma, "beta:", beta)
    return alpha, beta, gamma

if __name__ == "__main__":
    from multiprocessing import Pool
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("start", metavar="START", type=int)
    parser.add_argument("stop", metavar="STOP", type=int)
    parser.add_argument("step", metavar="SETP", nargs="?", default=1, type=int)
    parser.add_argument("-n", dest="nproc",
                        default=1, type=int,
                        help="Number of processes used to calculate result")
    parser.add_argument("-p", dest="plot",
                        default=False, action="store_true",
                        help="Directly plot results")
    args = parser.parse_args()

    if args.plot:
        import matplotlib.pyplot as plt

    p = Pool(args.nproc)
    res = []
    xs = range(args.start, args.stop, args.step)
    res = p.map(calc_greek, xs)
    ar = np.array([[gs] + list(data) for gs, data in zip(xs, res)])

    print("==========================")
    print("Alphas:", ar[:,1])
    if args.plot: 
        plt.figure()
        plt.title("Alpha")
        plt.xlabel("Grid size")
        plt.ylabel("Alpha")
        plt.plot(xs, ar[:,1], 'gx')
        plt.savefig("alpha.pdf")
    print("Betas: ", ar[:,2])
    if args.plot:
        plt.figure()
        plt.title("Beta")
        plt.xlabel("Grid size")
        plt.ylabel("Beta")
        plt.plot(xs, ar[:,2], 'rx')
        plt.savefig("beta.pdf")
    print("Gammas:", ar[:,3])
    if args.plot:
        plt.figure()
        plt.title("Gamma")
        plt.xlabel("Grid size")
        plt.ylabel("Gamma")
        plt.plot(xs, ar[:,3], 'bx')
        plt.savefig("gamma.pdf")
    np.savetxt("result.txt", ar)

    #if args.plot:
    #    plt.show()
