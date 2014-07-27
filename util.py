import sys
from byteplay3 import Code, Label, isopcode
import byteplay3 as byteplay

def simplememo(fn):
    '''Ignores any arguments to a function'''
    cachename='_'+fn.__name__
    def memofn(self,*args):
        res=getattr(self,cachename,None)
        if res is None:
            res=fn(self,*args)
            setattr(self,cachename,res)
        return res
        #if not hasattr(self,cachename):
        #    setattr(self,cachename,fn(self,*args))
        #return getattr(self,cachename)
    return memofn

def AutoEQ(cls):
    assert hasattr(cls,'__key__'), 'class %s has no key'%str(cls)
    def __eq__(self,other):
        return self is other or (
            type(self)==type(other) and
            all(a==b for a,b in zip(self.__key__(),other.__key__())))
    def __hash__(self):
        res=hash(type(self))
        for k in self.__key__():
            res*=13
            res+=hash(k)
        return res

    cls.__eq__=__eq__
    cls.__hash__=__hash__
    return cls

def AutoEQImmutable(cls):
    cls=AutoEQ(cls)
    cls.__hash__=simplememo(cls.__hash__)
    return cls

@AutoEQImmutable
class ExtraCode(Code):
    def __repr__(self):
        return self.name
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def __key__(self):
        yield self.filename
        yield self.firstlineno

def toset(a):
    if isinstance(a,set):
        return a
    else:
        return {a}

def fromset(res):
    if len(res)==1:
        return res.pop()
    return res

def excepthook(type,value,tb):
    import traceback, pdb
    # we are NOT in interactive mode, print the exception...
    traceback.print_exception(type, value, tb)
    print
    # ...then start the debugger in post-mortem mode.
    pdb.pm()
sys.excepthook=excepthook
