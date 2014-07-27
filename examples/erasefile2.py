import sys
from typer import *
from library import *

def erasefile():
    print('file erased.')

def main():
    global x
    erasefile()
    if randbool(None):
        x='abc'
    else:
        x=34
    if randbool(None):
        usestr(x)
        usenum(x)
    else:
        usenum(x)
        usestr(x)

