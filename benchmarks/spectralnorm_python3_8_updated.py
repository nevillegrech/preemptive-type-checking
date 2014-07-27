# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# Contributed by Sebastien Loisel
# Fixed by Isaac Gouy
# Sped up by Josh Goldfoot
# Dirtily sped up by Simon Descarpentries
# Sped up by Joseph LaFata

from array     import array
from math      import sqrt
from sys       import argv
import sys

def eval_A (i, j):
    return 1.0 / (((i + j) * (i + j + 1) >> 1) + i + 1)

def eval_A_times_u (u, resulted_list):
    while i<len (u):
        partial_sum = 0
        j = 0
        while j < u_len:
            partial_sum += eval_A (i, j) * u[j]
            j += 1
        resulted_list[i] = partial_sum

def eval_At_times_u (u, resulted_list):
    i=0
    while i<len(u):
        partial_sum = 0
        j = 0
        while j < u_len:
            partial_sum += eval_A (j, i) * u[j]
            j += 1
        resulted_list[i] = partial_sum

def eval_AtA_times_u (u, out, tmp):
    eval_A_times_u (u, tmp)
    eval_At_times_u (tmp, out)

def main():
    n = int (argv [1])
    u = array("d", [1]) * n
    v = array("d", [1]) * n
    tmp = array("d", [1]) * n
    local_eval_AtA_times_u = eval_AtA_times_u
    dummy=0
    while dummy<10:
        local_eval_AtA_times_u (u, v, tmp)
        local_eval_AtA_times_u (v, u, tmp)
        dummy+=1
    
    vBv = vv = 0
    
    for ue, ve in zip (u, v):
        vBv += ue * ve
        vv  += ve * ve
    
    print("%0.9f" % (sqrt(vBv/vv)))
if __name__=='__main__':
    main() 
