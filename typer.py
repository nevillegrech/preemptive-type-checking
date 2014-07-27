'''
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Author: Neville Grech
'''


from itertools import chain
from collections import defaultdict
from util import *
from mytypes import *

PREVIOUS_STACK='previous_stack'

def typetostr(t):
    'Returns a textual representation of a type.'
    if isinstance(t,type):
        return str(t).split("'")[1]
    if isinstance(t,str):
        return t
    if isinstance(t,set):
        return ' or '.join(typetostr(tt) for tt in t)
    assert False,t

def typejoin(*types):
    '''Returns a join of the types given as arguments.'''
    # optimization, chose 2 on purpose
    if len(types)<2: return types[0]
    res=set()
    for t in types:
        if isinstance(t,set):
            res|=t
        else:
            res.add(t)
    if Top in res: return Top
    res-={Bot}
    if len(res)==1: return res.pop()
    if not res: return Bot
    return res

def typemeet(u,v):
    '''Returns a meet of the types given as arguments.'''
    if u == v: return u
    if u==Top: return v
    if v==Top: return u
    res=(u if isinstance(u,set) else {u}) & (v if isinstance(v,set) else {v})
    if not res: return Bot
    if len(res)==1: return res.pop()
    return res

class Name:
    '''Base class for variable names/stack position hierarchy'''
    isstack,islocal,isglobal=False,False,False
    def shift(self,n):
        return self
    def addtodom(self,a):
        pass

@AutoEQImmutable
class VName(Name):
    '''Base class for a variable name.'''
    def __init__(self,x):
        self.x=x
    def __key__(self):
        yield self.x
    def addtodom(self,a):
        a.add(self)
    def __repr__(self):
        return self.x

class Global(VName): isglobal=True
class Local(VName): islocal=True

@AutoEQImmutable
class StackOffset(Name):
    '''Represents the offset on a stack.'''
    isstack,islocal,isglobal=True,False,False
    def __init__(self,n):
        self.n=n
    def shift(self,n):
        if n==0: return self
        else: return StackOffset(self.n+n)
    def __key__(self):
        yield self.n
    def __str__(self):
        if self.n:
            return 'StackOffset(%d)'%self.n
        else: return ''
    __repr__=__str__

tos=StackOffset(0)
tos1=StackOffset(1)

class BaseInst:
    checks=0
    changesprog=False
    def __init__(self,analyser,s):
        self.analyser=analyser
        self.s=s

class FirstInst(BaseInst):
    '''Represents the instruction at first execution point (),
    which in reality does not exist.'''
    def gtp(self,x):
        if not x.isglobal:
            return Un
        # x is a global
        globs=self.analyser.globs
        if x.x in globs:
            val=globs[x.x]
        elif x.x in self.analyser.builtins:
            val=self.analyser.builtins[x.x]
        else:
            return Un
        return self.analyser.gettype(val)

    def gtf(self,x):
        return Top

    def _getnext(self):
        return [self.analyser.initpoint]

    def _getnextloc(self):
        return [None]
class LastInst(BaseInst):
    '''Represents the instruction at first execution point None,
    which in reality does not exist.'''
    def gtf(self,x):
        return Top
    def gtp(self,x):
        return Un
    def _getnext(self):
        return []
    _getnextloc=_getnext


class Inst(BaseInst):
    '''This class represents a generic instruction object.
    All subclasses of Inst correspond to actual bytecode instructions.

    This contains all the functionality for inferring the types at its curent
    point.'''
    def __init__(self,analyser,s):
        super().__init__(analyser,s)
        (p,pc)=self.s[-1]
        self.operand=p.code[pc][1]
    def shiftp(self,x):
        '''Depending on the stack shifting of the current instruction
        shifts the stack offset for the forwards analysis'''
        return x.shift(-self.stackshift)
    def shiftf(self,x):
        '''Depending on the stack shifting of the current instruction
        shifts the stack offset for the backwards analysis'''
        return x.shift(self.stackshift)
    def getfunction(self,n):
        '''Returns the function loaded at stack position n'''
        assert n!=0
        a=self.analyser
        prev=list(a.getprevloc(self.s))
        assert len(prev)==1,prev
        prev=a.getinst(prev[0])
        return prev.getfunction(n-self.stackshift)

    def _getnext(self):
        '''Default implementation that returns the next execution point.
        By default this is the next instruction in program order.'''
        a=self.analyser
        *next, (p,pc)=self.s
        next.append((p,pc+1))
        return [a.skipinvalid(next)]
    _getnextloc=_getnext
    def gtp(self,x):
        '''Returns the p type of x at the point associated with
        the current instruction.'''
        a=self.analyser
        spotify=a.spotify
        s=self.s
        spot=(s,x)
        if spot in a.cachep:
            size,typ=a.cachep[spot]
            if typ!=Bot:
                return typ
        assert not (x.isstack and x.n<0)
        if spotify(spot) in a.trail:
            return Bot
        a.trail.add(spotify(spot))
        x.addtodom(a.dom[self.s])
        size,typ=len(a.trail),self._gtp(x)
        if typ is None:
            x=self.shiftp(x)
            if x.isglobal or x==tos:
                typ=self.gtpprevglob(x)
            elif x.islocal or x.isstack:
                typ=self.gtpprevloc(x)
            else:
                assert False
        a.trail.remove(spotify(spot))
        a.cachep[spot]=(size,typ)
        return typ

    def gtf(self,x):
        '''Returns the f type of x at the point associated with
        the current instruction.'''
        a=self.analyser
        spotify=a.spotify
        s=self.s
        spot=(s,x)
        if spot in a.cachef:
            size,typ=a.cachef[spot]
            if typ!=Bot:
                return typ
        if x.isstack and x.n<0:
            return Top
        assert not (x.isstack and x.n>10)
        if spotify(spot) in a.trail:
            return Bot
        a.trail.add(spotify(spot))
        size,typ=len(a.trail),self._gtf(x)
        if typ is None:
            x=self.shiftf(x)
            typ=self.gtfnext(x)
        a.trail.remove(spotify(spot))
        a.cachef[spot]=(size,typ)
        if typ!=Top:
            x.addtodom(a.dom[self.s])
        return typ

    def _gtp(self,x):
        pass
    def _gtf(self,x):
        pass
    def gtpprevloc(self,x):
        '''Returns a union of the p types of x at the previous points
        on the intra procedural control flow graph'''
        a=self.analyser
        s=self.s
        if a.isentry(s):
            assert x.islocal
            args=s[-1][0].args
            name=x.x
            if name not in args:
                return Un
            index=len(args)-1-args.index(name)
            prev=a.getprev(s)
            if index==0:
                return typejoin(*[a.getinst(s_).gtpprevglob(tos)
                                  for s_ in prev])
            else:
                return typejoin(*[a.getinst(s_).gtpprevloc(StackOffset(index))
                                  for s_ in prev])
        prev=a.getprevloc(s)
        if not prev:
            return Un
        return typejoin(*[a.getinst(s_).gtp(x) for s_ in prev])

    def gtpprevglob(self,x):
        '''Returns a union of the p types of x at the previous points
        on the inter procedural control flow graph'''
        s=self.s
        a=self.analyser
        prev=a.getprev(s)
        return typejoin(*[a.getinst(s_).gtp(x) for s_ in prev])

    def gtfnext(self,x):
        a=self.analyser
        nxt=a.getnext(self.s)
        assert nxt
        return typejoin(*[a.getinst(s_).gtf(x) for s_ in nxt])
    def __repr__(self):
        return '%s %s at %s'%(type(self),self.operand,self.s)
    __str__=__repr__

class LOAD_CONST(Inst):
    stackshift=1
    def getfunction(self,n):
        if n!=0:
            return super().getfunction(n)
        return self.operand

    def _gtp(self,x):
        if x==tos:
            *rst, (p,pc)=self.s
            return self.analyser.gettype(self.operand)

class MAKE_FUNCTION(Inst):
    stackshift=-1
    def _gtp(self,x):
        if x==tos:
            return Callable

class DUP_TOP(Inst):
    stackshift=1
    def _gtp(self,x):
        if x==tos:
            return self.gtpprevglob(tos)
    def _gtf(self,x):
        return # TODO
        if x==tos:
            #return Top
            return typemeet(self.gtfnext(tos),self.gtfnext(tos1))

      
class CALL_FUNCTION(Inst):
    @property
    def checks(self):
        return 1+(0 if self.changesprog else self.operand)
    @property
    def stackshift(self):
        return -self.operand
    def shiftp(self,x):
        if x==tos:
            return tos
        else:
            return super().shiftp(x)
    def getfunction(self,n):
        assert n!=0
        a=self.analyser
        prev=list(a.getprevloc(self.s))
        assert len(prev)==1,prev
        prev=a.getinst(prev[0])
        return prev.getfunction(n+self.operand)

    @simplememo
    def getcalledfn(self):
        a=self.analyser
        prev=a.getprevloc(self.s)
        assert len(prev)==1,self.s
        res=a.getinst(list(prev)[0]).getfunction(self.operand)
        return res

    @property
    def changesprog(self):
        return not getattr(self.getcalledfn(),'__annotations__',False)

    def _gtp(self,x):
        fn=self.getcalledfn()
        if getattr(fn,'__annotations__',False) and x==tos:
            return fn.__annotations__['return']

    def _gtf(self,x):
        fn=self.getcalledfn()
        a=self.analyser
        s=self.s
        if x.isstack:
            n=x.n
            n_args=self.operand
            if n<n_args:
                if n<n_args and hasattr(fn,'__code__'):
                    args=ExtraCode.from_code(fn.__code__).args
                    assert len(args)==n_args
                    name=args[n_args-n-1]
                    if getattr(fn,'__annotations__',False):
                        assert name in fn.__annotations__,'all or none'
                        return fn.__annotations__[name]
                    next=a.getnext(s)
                    return self.gtfnext(Local(name))
            if n==n_args:
                return Callable
        if x.islocal or x.isstack:
            return typejoin(*[a.getinst(nxt).gtf(self.shiftf(x)) for nxt in a.getnextloc(self.s)])

    def _getnext(self):
        if not self.changesprog:
            return self._getnextloc()
        # get called function
        a=self.analyser
        f=self.getcalledfn()
        p_=ExtraCode.from_code(f.__code__)
        return [a.skipinvalid((self.s+((p_,0),))[-a.accuracy:])]

class POP_JUMP_IF_FALSE(Inst):
    checks=1
    stackshift=-1
    def _gtf(self,x):
        if x==tos:
            return typejoin(bool,Number)
    def _getnext(self):
        return super()._getnext()+JUMP_ABSOLUTE._getnext(self)
    _getnextloc=_getnext

class STORE_GLOBAL(Inst):
    stackshift=-1
    def _gtp(self,x):
        if x.isglobal and x.x==self.operand:
            return self.gtpprevglob(tos)
    def _gtf(self,x):
        if x==tos:
            return self.gtfnext(Global(self.operand))
        if x.isglobal and x.x==self.operand:
            return Top
            
class STORE_FAST(Inst):
    stackshift=-1
    def _gtp(self,x):
        if x.islocal and x.x==self.operand:
            return self.gtpprevglob(tos)
    def _gtf(self,x):
        if x==tos:
            return self.gtfnext(Local(self.operand))
        if x.islocal and x.x==self.operand:
            return Top

class LOAD_GLOBAL(Inst):
    stackshift=1
    def _gtf(self,x):
        if x.isglobal and x.x==self.operand:
            return self.gtfnext(tos)#typemeet(self.gtfnext(tos),x)
        #TODO meet not working
    def _gtp(self,x):
        if x==tos:
            return self.gtpprevglob(Global(self.operand))
    def getfunction(self,n):
        if n!=0:
            return super().getfunction(n)
        a=self.analyser
        f=self.operand
        if f in a.globs:
            return a.globs[f]
        if f in a.builtins:
            return a.builtins[f]
        raise Exception('%s not found'%f)

class LOAD_FAST(Inst):
    stackshift=1
    def _gtf(self,x):
        if x.islocal and x.x==self.operand:
            return self.gtfnext(tos)
    def _gtp(self,x):
        if x==tos:
            return self.gtpprevloc(Local(self.operand))

class POP_TOP(Inst): stackshift=-1

class NOP(Inst): stackshift=0

class POP_BLOCK(NOP): pass

class SETUP_LOOP(NOP): pass

class BREAK_LOOP(NOP):
    def _getnext(self):
        *rst, (p,pc)=self.s
        for _pc in range(pc-1,0,-1):
            if p.code[_pc][0]==byteplay.SETUP_LOOP:
                label=p.code[_pc][1]
                for _pc in range(pc+1,len(p.code)):
                    if p.code[_pc][0]==label:
                        return [self.analyser.skipinvalid(rst+[(p,_pc)])]
                assert False
        assert False
        _getnextloc=_getnext

class JUMP_ABSOLUTE(NOP):
    def _getnext(self):
        *rst, (p,pc)=self.s
        for i,label in enumerate(p.code):
            if label==(p.code[pc][1],None):
                rst.append((p,i))
                return [self.analyser.skipinvalid(rst)]
        assert False
    _getnextloc=_getnext

class JUMP_FORWARD(JUMP_ABSOLUTE): pass

class POP_JUMP_IF_TRUE(POP_JUMP_IF_FALSE): pass

class RETURN_VALUE(Inst):
    stackshift=0
    changesprog=True
    def _getnext(self):
        a=self.analyser
        *start, (p,pc)=self.s
        start.append((p,0))
        return chain(*(a.getinst(fro)._getnextloc() for fro in a.getprev(a.skipinvalid(start))))
    def _getnextloc(self):
        return []
    def _gtf(self,x):
        if x==tos or x.isglobal:
            return self.gtfnext(x)
        return Top

class INPLACE_ADD(Inst):
    checks=2
    stackshift=-1
    def _gtp(self,x):
        if x==tos: return Number

    def _gtf(self,x):
        if x in (tos,tos1): return Number

class BINARY_MODULO(Inst):
    checks=2
    stackshift=-1
    def _gtp(self,x):
        if x==tos: return self.gtpprevloc(tos1)
    def _gtf(self,x):
        if x in (tos,tos1): return {Number,str}


BINARY_OR=BINARY_LSHIFT=BINARY_RSHIFT=BINARY_AND=\
INPLACE_RSHIFT=BINARY_FLOOR_DIVIDE=INPLACE_SUBTRACT=\
BINARY_TRUE_DIVIDE=BINARY_MULTIPLY=INPLACE_MULTIPLY=\
BINARY_POWER=BINARY_SUBTRACT=BINARY_LSHIFT=BINARY_ADD=INPLACE_ADD

class UNARY_NEGATIVE(Inst):
    stackshift=0
    checks=1
    def _gtp(self,x):
        if x==tos: return Number

    def _gtf(self,x):
        if x==tos: return Number

class BUILD_TUPLE(Inst):
    @property
    def stackshift(self):
        return -self.operand+1
    def _gtp(self,x):
        if x==tos:
            return tuple
    def _gtf(self,x):
        if x.isstack and x.n<self.operand:
            return Top

class UNPACK_SEQUENCE(Inst):
    checks=1
    @property
    def stackshift(self):
        return self.operand-1

    def _gtp(self,x):
        if x.isstack and x.n<self.operand: return Top

    def _gtf(self,x):
        if x==tos: return tuple

class COMPARE_OP(INPLACE_ADD):
    def _gtp(self,x):
        if x==tos: return bool

class BINARY_SUBSCR(Inst):
    stackshift=-1
    checks=1
    def _gtp(self,x):
        if x==tos: return Top
    def _gtf(self,x):
        if x==tos: return Number
        if x==tos1: return MutableSequence

class TypeErrorAssertion(AssertionError): pass

class Analyser:
    '''This class is the entry point for the analysis.'''
    def __init__(self,main, accuracy=2,
                 spotify=lambda b:b[0]):
        self.spotify=spotify
        self.accuracy=accuracy
        self.main=main
        self.globs=main.__globals__
        self.builtins=__builtins__
        self.initpoint=((ExtraCode.from_code(self.main.__code__),1),)
        self.localedges=set()
        self.nextlocaldict=defaultdict(set)
        self.prevlocaldict=defaultdict(set)
        self.edges=set()
        self.nextdict=defaultdict(set)
        self.prevdict=defaultdict(set)
        self.getnext=self.nextdict.__getitem__
        self.getprev=self.prevdict.__getitem__
        self.getnextloc=self.nextlocaldict.__getitem__
        self.getprevloc=self.prevlocaldict.__getitem__
        self.points={(),self.initpoint,None}
        self.trail=set()
        self.dom=defaultdict(set)
        self.cachep={}
        self.cachef={}
        self.failedges={}
        self.instdict={():FirstInst(self,()),None:LastInst(self,None)}
        self.assertions=defaultdict(list)
        self.calcedges()
        self.calcassertions()

    def printwarnings(self):
        i=1
        for warn in self.failedges.values():
            print('Failure',i,'- partial Traceback:')
            print(warn)
            print()
            i+=1
        for (fro,to),ass in self.assertions.items():
            print('Assertion ',i)
            print(self.pointToStr(to))
            for x,t in ass:
                print('Variable %s expected %s'%(x,typetostr(t)))
    def isentry(self,s):
        return s[-1][1]==1 and isinstance(
            self.getinst(list(self.getprev(s))[0]),CALL_FUNCTION)
    def gettype(self,val):
        for typ in (Callable,Number,MutableSequence,type(val)):
            if isinstance(val,typ): return typ

    def getinst(self,point):
        si=self.instdict
        if point not in si:
            p,pc=point[-1]
            si[point]=globals()[str(p.code[pc][0])](self,point)
        return si[point]

    def calcedges(self):
        oldlen=-1
        spa=self.points.add
        points=self.points
        sea=self.edges.add
        se=self.edges
        sn=self.nextdict
        sp=self.prevdict
        slea=self.localedges.add
        sle=self.localedges
        sln=self.nextlocaldict
        slp=self.prevlocaldict
        while oldlen!=len(se):
            oldlen=len(se)
            for point in set(points):
                for nextpoint in self.getinst(point)._getnext():
                    edge=(point,nextpoint)
                    if edge in se:
                        continue
                    spa(nextpoint)
                    sea(edge)
                    sn[point].add(nextpoint)
                    sp[nextpoint].add(point)
                if sln[point]:
                    continue
                for nextpoint in self.getinst(point)._getnextloc():
                    edge=(point,nextpoint)
                    if edge in sle:
                        continue
                    slea(edge)
                    sln[point].add(nextpoint)
                    slp[nextpoint].add(point)
        # optimisation, instructions have all been constructed
        # replace factory with call to dictionary
        self.getinst=self.instdict.get
    def skipinvalid(self,point):
        *rst, (p,pc)=point
        while not isopcode(p.code[pc][0]):
            pc+=1
        assert pc<len(p.code)
        rst.append((p,pc))
        return tuple(rst)
    def pointToStr(self,point):
        res=[]
        for p,pc in point:
            for i in range(pc,-1,-1):
                op,operand=p.code[i]
                if op==byteplay.SetLineno:
                    res.append('File "%s", line %d, in %s'%(p.filename,operand,p.name))
                    break
        return '\n'.join(res)
    def emit(self,globs):
        newfns=set()
        b=byteplay # alias
        insertions=defaultdict(list)
        def insertss(s):
            # inserts before
            insertions[s]+=[
                (b.LOAD_CONST,s),
                (b.STORE_GLOBAL,PREVIOUS_STACK)
            ]
        def insertfail(s,sprev):
            failmsg=self.failedges[sprev,s]
            def failfast(globs):
                if globs[PREVIOUS_STACK]!=sprev:
                    return
                raise TypeErrorAssertion(failmsg)
            insertions[s]+=[
                (b.LOAD_CONST,failfast),
                (b.LOAD_GLOBAL,'globals'),
                (b.CALL_FUNCTION,0),
                (b.CALL_FUNCTION,1),
                (b.POP_TOP,None)
            ]
        def insertassert(s,assertion,sprev):
            def asserttype(globs,locs):
                x,t=assertion
                if globs[PREVIOUS_STACK]!=sprev:
                    return
                dic=locs if x.islocal else globs
                if x.x not in dic:
                    tr=Un
                else:
                    tr=self.gettype(dic[x.x])
                if typemeet(tr,t)!=Bot:
                    return
                raise TypeErrorAssertion('Future type error due to %s at %s, expected %s got %s'%(x,s,typetostr(t),typetostr(tr)))
            insertions[s]+=[
                (b.LOAD_CONST,asserttype),
                (b.LOAD_GLOBAL,'globals'),
                (b.CALL_FUNCTION,0),
                (b.LOAD_GLOBAL,'locals'),
                (b.CALL_FUNCTION,0),
                (b.CALL_FUNCTION,2),
                (b.POP_TOP,None)
             ]
        def getfname(s):
            *rst,(p,pc)=s
            fname='_'.join(p.name+str(pc) for p,pc in rst)
            fname+='_'+p.name
            return fname

        for point in self.points:
            if point:
                *rst,(p,pc)=point
                rst.append(p)
                newfns.add(tuple(rst))
        # insert marker at entry point
        insertions[self.initpoint]+=[
                (b.LOAD_CONST,()),
                (b.STORE_GLOBAL,PREVIOUS_STACK)
        ]
        for edge in self.edges:
            fro,to=edge
            if edge in self.failedges:
                for s in self.getprev(to):
                    insertss(s)
                insertfail(to,fro)
            if edge in self.assertions:
                for s in self.getprev(to):
                    insertss(s)
                for assertion in self.assertions[edge]:
                    insertassert(to,assertion,fro)
        self.delfns={PREVIOUS_STACK}
        self.checks=0
        for fn in newfns:
            *rst,p=fn
            newbc=ExtraCode.from_byteplay_code(p)
            # create new bytecode
            newbc.code=[]
            for pc in range(len(p.code)):
                s=tuple(rst+[(p,pc)])
                if isopcode(p.code[pc][0]):
                    if self.getinst(s):
                        self.checks+=self.getinst(s).checks
                newbc.code+=insertions[s]
                # change called function reference
                op,operand=p.code[pc]
                if op==b.CALL_FUNCTION:
                    _s=list(self.getnext(s))[0]
                    if self.isentry(_s):
                        # change called function
                        newbc.code[-operand-1]=(b.LOAD_GLOBAL,getfname(_s))
                newbc.code.append(p.code[pc])
            self.delfns.add(getfname(s))
            globs[getfname(s)]=FunctionType(newbc.to_code(),globs)

    def clearfns(self,globs):
        for fn in self.delfns:
            if fn in globs:
                del globs[fn]
    def calcassertions(self):
        # populate domains
        def traverse(point,allpoints,nxtfn,gt):
            if point not in allpoints:
                return
            gt(point)
            allpoints.remove(point)
            for point in nxtfn(point):
                traverse(point,allpoints,nxtfn,gt)
        # traverse forwards direction
        traverse((),set(self.points),self.getnext,
                 lambda p : self.getinst(p).gtp(tos))
        # traverse backwards direction
        traverse(None,set(self.points),self.getprev,
                 lambda p : self.getinst(p).gtf(tos))
        gi=self.getinst
        # calculate failedge
        for edge in self.edges:
            fro,to = edge
            froinst=gi(fro)
            for x in self.dom[to] | {tos}:
                if x.islocal and froinst.changesprog: continue
                _tf=gi(to).gtf(x)
                if _tf==Top: continue
                tp=froinst.gtp(x);tf=froinst.gtf(x)
                if tf!=_tf and typemeet(tp,_tf)==Bot:
                    self.failedges[edge]='%s\nVariable %s expected %s but found %s'%(self.pointToStr(to),x,typetostr(_tf),typetostr(tp))
        # add to failedge
        oldsize=0
        while oldsize!=len(self.failedges):
            oldsize=len(self.failedges)
            for edge in self.edges:
                if edge in self.failedges:
                    continue
                # if all next edges are failedges then this one is
                fro,to=edge
                if to is not None and all((to,nxt) in self.failedges
                       for nxt in self.getnext(to)):
                    self.failedges[edge]='\n'.join({
                        self.failedges[(to,nxt)]
                        for nxt in self.getnext(to)})
        # calculate assertions to insert
        # fail edges is at its maximum here

        for edge in self.edges:
            if edge in self.failedges:
                continue
            fro,to=edge
            if len(self.getnext(fro))==1:
                continue
            froinst=gi(fro)
            toinst=gi(to)
            for x in self.dom[to]:
                if x.islocal and froinst.changesprog:
                    continue
                _tf=toinst.gtf(x)
                tp=froinst.gtp(x);tf=froinst.gtf(x)
                meet=typemeet(tp,_tf)
                if tf!=_tf and meet!=tp and meet!=Bot:
                    self.assertions[edge].append((x,meet))
        # remove redundant failedge
        oldsize=9999999999
        oldfailedges=dict(self.failedges)
        while oldsize!=len(self.failedges):
            oldsize=len(self.failedges)
            for edge in dict(self.failedges):
                # if all previous edges are failedges then this one
                # need not be
                fro,to=edge
                if fro!=() and all(
                    (prev,fro) in oldfailedges
                    for prev in self.getprev(fro)):
                    self.failedges.pop(edge)
