# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Tupteq
# 2to3 - fixed by Daniele Varrazzo

import sys
sys.path.append('..')
from typer import Analyser,ExtraCode,Number,NoneType
from library import *
from sys import argv
sys.setrecursionlimit(400000)

#size = int(sys.argv[1])
def cout(a:{bytes,bytearray}) -> NoneType:
    sys.stdout.buffer.write(a)

def main():
    bit = 128
    byte_acc = 0
    size = float(argv[1])
    cout(b'P4\n') # TODO
    y=0
    x=0
    while y<size:
        fy = 2j * y / size - 1j
        while x<size:
            z = 0j
            c = 2. * x / size - 1.5 + fy
            i=0
            while i<50:
                z = z * z + c
                if abs(z) >= 2.0:
                    break
                i+=1
            else:
                byte_acc += bit

            if bit > 1:
                bit >>= 1
            else:
                cout((byte_acc,))
                bit = 128
                byte_acc = 0

        if bit != 128:
            bit = 128
            byte_acc = 0
            cout((byte_acc,))
        y+=1

if __name__=='__main__':
    argv=['',1]
    #main() #uncomment to get previous behavior
    a=Analyser(main)
    a.printwarnings()
    a.emit(globals())
    _main()

