from mytypes import *
from random import random

oldprint=print
def print(s:Top,s2:Top) -> NoneType:
    return oldprint(s,s2)

oldinput=input
def input(s:str) -> str:
    return input(s)

oldlen=len
def len(a:{str,MutableSequence}) -> Number:
    return oldlen(a)

oldfloat=float
def float(n:Top) -> Number:
    return oldfloat(n)

oldabs=abs
def abs(n:Number) -> Number:
    return oldabs(n)

def randbool(n:NoneType) -> bool:
    assert n==None
    return random()<0.5

def usenum(x:Number) -> NoneType:
    if not isinstance(x,Number):
        raise TypeError('Expected number, got %s'%(repr(x)))

def usestr(s:str) -> NoneType:
    if not isinstance(s,str):
        raise TypeError('Expected str')

def concat(a:str,b:str) -> str:
    return a+b

def slice(s:str,start:Number,end:Number) -> str:
    return s[start:end]

xrange=range
def range(n:Number) -> MutableSequence:
    return list(xrange(n))

def map(f:Callable,m:MutableSequence) -> MutableSequence:
    return [f(i) for i in m]
xmax=max
def max(m:MutableSequence) -> {MutableSequence,Number}:
    return xmax(m)

xlist=list
def list(o:{tuple,MutableSequence,str}) -> MutableSequence:
    return xlist(o)

xint=int
def int(o:Top) -> Number:
    return xint(o)

def sort(o:MutableSequence) -> NoneType:
    o.sort()

xmin=min
def min(o:MutableSequence) -> {MutableSequence,Number}:
    return xmin(o)

def lstgetstr(m:MutableSequence,n:int) -> str:
    ret=m[n]
    assert isinstance(ret,str)
    return ret

def tostr(s:Top)->str:
    return str(s)

def lstgetnum(m:MutableSequence,n:Number) -> Number:
    ret=m[n]
    assert isinstance(ret,Number)
    return ret

def lstgetlst(m:MutableSequence,n:Number) -> MutableSequence:
    ret=m[n]
    assert isinstance(ret,MutableSequence)
    return ret

def lstsetnum(m:MutableSequence,n:Number,v:Number) -> NoneType:
    m[n]=v

def join(s:str,l:MutableSequence) -> str:
    return s.join(l)

def append(l:MutableSequence,o:Top) -> NoneType:
    l.append(o)

def printchars(s:Top)->NoneType:
    print(s,end='')
