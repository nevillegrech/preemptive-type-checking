#! /usr/bin/python3.3
import sys
sys.path.append('..')
from typer import Analyser
from library import *
from dis import dis

def erasefile():
    # ...
    print('file erased: ',toerase)

def f():
    global x,toerase
    if randbool(None):
        toerase='xyz'
        erasefile()
        x+1

def main():
    global x
    x=''
    f()
    x=5
    f()

if __name__=='__main__':
    a=Analyser(main,accuracy=2)
    a.printwarnings()
