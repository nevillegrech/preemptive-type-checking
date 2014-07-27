import sys
if __name__=='__main__':
    sys.path.append('..')
from library import *
from typer import *
from dis import dis

def fixit():
    global x1, x2, x3
    if randbool(None):
        usenum(x1)
        usenum(x2)
        usenum(x3)
        return
    x1=x2
    x2=x3
    x3=5
    return fixit()

def main():
    global x1,x2,x3
    x1=x2=x3=None
    fixit()


if __name__=='__main__':
    a=Analyser(main,accuracy=4,spotify=lambda a:a)
    a.printwarnings()
