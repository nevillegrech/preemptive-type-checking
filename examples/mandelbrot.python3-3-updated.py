import sys
sys.path.append('..')
from typer import Analyser,Number,NoneType
sys.setrecursionlimit(400000)

#size = int(sys.argv[1])
def cout(a:{bytes,bytearray}) -> NoneType:
    sys.stdout.buffer.write(a)

size=10
def main():
    global size, bit, byte_acc, x,y,z,fy
    bit = 128
    byte_acc = 0
    print('P4\n',size)
    print(' ',size)
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
                out=(byte_acc,)
                cout(out)
                bit = 128
                byte_acc = 0

        if bit != 128:
            out=(byte_acc,)
            cout(out)
            bit = 128
            byte_acc = 0
        y+=1
# main()
a=Analyser(main)
a.printwarnings()
a.emit(globals())
_main()

