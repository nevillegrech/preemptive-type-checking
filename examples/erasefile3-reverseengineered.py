'''This is (approimately) how erasefile3 would look like with preemptive
type checking enabled, at a source code representation.
'''
import sys
sys.path.append('..')
from typer import *
from dis import dis

def erasefile(f):
    print(f,'erased')

def foo():
    erasefile('file5')
    usenum(x)
def main():
    global x
    erasefile('file1')
    if randbool(None):
        raise TypeErrorAssertion('Variable x expected numbers.Number but got str')
        erasefile('file2')
        x='abc'
    else:
        erasefile('file3')
        x=34
    erasefile('file4')
    foo()
