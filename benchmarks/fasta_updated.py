# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# modified by Ian Osgood
# modified again by Heinrich Acker
# 2to3

# modified for use with preemptive type checking by Neville

import sys, bisect
from sys import argv,path
path.append('..')
from library import *
from typer import Analyser
from dis import dis

alu = (
   'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
   'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
   'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
   'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
   'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
   'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
   'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA')

iub = list(zip('acgtBDHKMNRSVWY', [0.27, 0.12, 0.12, 0.27] + [0.02]*11))

homosapiens = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


def genRandom(lim, ia = 3877, ic = 29573, im = 139968):
    seed = 42
    imf = float(im)
    while 1:
        seed = (seed * ia + ic) % im
        yield lim * seed / imf

Random = genRandom(1.)

def gR()->Number:
    return Random.__next__()
def makeCumulative(table:MutableSequence)->tuple:
    P = []
    C = []
    prob = 0.
    for char, p in table:
        prob += p
        P += [prob]
        C += [char]
    return (P, C)


def repeatFasta(src,n):
    r = len(src)
    s = concat(src,src)
    s = concat(s, slice(src,0,n % r))
    j=0
    while j<(n // width):
        i = j*width % r
        print(slice(s,i,i+width),'')
        j+=1
    if n % width:
        print(slice(s,-(n % width),999),'')

bb = bisect.bisect
width = 60

def randomFasta(table, n):
    global probs, chars
    probs,chars=makeCumulative(table)
    j=0
    while j<(n // width):
        print(join('',map(lambda x : lstgetstr(chars,bb(probs, gR())),
                          range(width))),'')
    if n % width:
        print(join('',map(lambda x : lstgetstr(chars,bb(probs, gR())),
                          range(n % width))),'')

def main():
    print('>ONE Homo sapiens alu','')
    repeatFasta(alu, 2)

    print('>TWO IUB ambiguity codes','')
    randomFasta(iub, 3)

    print('>THREE Homo sapiens frequency','')
    randomFasta(homosapiens, 5)

if __name__=='__main__':
    a=Analyser(main)
    a.emit(globals())
    _main()
