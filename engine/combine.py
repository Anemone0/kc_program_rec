#!/usr/bin/env python
# -*-coding=utf-8-*-

from scipy.sparse import csr_matrix
def combine(md_sim,sc_sim, alpha=0.7,beta=0.3):
    return alpha*md_sim+beta*sc_sim

if __name__ == '__main__':
    pass
