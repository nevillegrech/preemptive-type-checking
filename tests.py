'''
Test suite for Preemptive type checking

Author: Neville Grech
'''

import sys
sys.setrecursionlimit(4000)
import unittest
from itertools import chain,tee
from dis import dis
from collections import defaultdict
from typer import *
from library import *
from mytypes import *

def isValidPoint(point):
    if point is None or len(point)==0:
        return True
    p,pc=point[-1]
    return isopcode(p.code[pc][0])

class VerifyNextPrevious:
    def testedges(self):
        edges=self.analyser.edges
        assert sum(to==None for fro,to in edges)==1
        assert sum(fro==() for fro,to in edges)==1
        # lastPos and firstPos have no next/previous
        assert sum(fro==None for fro,to in edges)==0
        assert sum(to==() for fro,to in edges)==0
        # to and from are not the same
        assert all(fro!=to for fro,to in edges)

class InferTest(unittest.TestCase):
    accuracy=2
    spotify=staticmethod(lambda a:a[0])
    def setUp(self):
        self.analyser=Analyser(self.main,accuracy=self.accuracy,spotify=self.spotify)

    def getPoint(self,lst):
        res=[]
        lst2=[]
        for i in range(len(lst)//2):
            lst2.append((lst[i*2],lst[i*2+1]))
        for f,pc in lst2:
            if f=='main':
                p=ExtraCode.from_code(self.main.__code__)
            else:
                if f not in self.analyser.globs:
                    assert False,'f not in self.analyser.globs'
                p=ExtraCode.from_code(self.analyser.globs[f].__code__)
            res.append((p,pc))
        res=tuple(res)
        assert isValidPoint(res),res
        return res

    def printMain(self):
        print('\n'.join('%d. %s %s'%(i,op,c) for i,(op,c) in enumerate(ExtraCode.from_code(self.main.__code__).code)))
    def printProg(self):
        pass #TODO
    def assertTypeP(self,s,x,t):
        assert self.getPoint(s) in self.analyser.points
        self.assertEqual(self.analyser.getinst(self.getPoint(s)).gtp(x),t)
    def assertTypeF(self,s,x,t):
        assert self.getPoint(s) in self.analyser.points
        self.assertEqual(self.analyser.getinst(self.getPoint(s)).gtf(x),t)
    def assertFailsOnEntry(self):
        self.assertEqual(set(self.analyser.failedges.keys()),
                         {((),self.getPoint(['main',1]))})

    def assertEdge(self,fro,to):
        assert (self.getPoint(fro),self.getPoint(to)) in self.analyser.edges
        assert (self.getPoint(fro),self.getPoint(to)) in self.analyser.localedges, self.analyser.localedges

class VerifyByteplay:
    def testbyteplay(self):
        codeobj=self.main.__code__
        t=ExtraCode.from_code(codeobj)
        u=ExtraCode.from_code(t.to_code())
        for (opcode1,operand1),(opcode2,operand2) in zip(t.code,u.code):
            if not (isinstance(opcode1,Label)):
                self.assertEqual((opcode1),(opcode2))
            if not (isinstance(operand1,Label)):
                self.assertEqual(operand1,operand2)

class VerifyTransformation(InferTest):
    max_iterations=10
    vars=['a']
    probabilityOfFail=0
    @staticmethod
    def main():
        pass
    def tearDown(self):
        for var in self.vars:
            for globs in (globals(),self.analyser.globs):
                if var in globs:
                    del globs[var]

    def testtransform(self):
        if self.probabilityOfFail in (0,1):
            self.max_iterations=2
        try:
            self.analyser.emit(globals())
            hasFailed=False
            hasNotFailed=False
            for i in range(self.max_iterations):
                try:
                    _main()
                except TypeErrorAssertion:
                    hasFailed=True
                    assert self.probabilityOfFail>0
                else:
                    hasNotFailed=True
                    assert self.probabilityOfFail<1
                if hasFailed and hasNotFailed:
                    break
            if 0<self.probabilityOfFail<1:
                assert hasFailed and hasNotFailed
        finally:
            self.analyser.clearfns(globals())


class Test(InferTest,VerifyByteplay,VerifyNextPrevious):
    accuracy=1
    def main():
        global x,y,z
        if randbool(None):
            x=5
        else:
            x='hello'
        usenum(x)
    def test_prev(self):
        self.assertEdge(['main',12],['main',15])
        self.assertEdge(['main',8],['main',15])
    def test_usenum(self):
        self.assertTypeF(['main',2],Global('usenum'),Callable)
    def test_x(self):
        self.assertTypeP(['main',20],Global('x'),{str,Number})

class TestMF(InferTest):
    def main():
        h()
    def test_x(self):
        self.assertTypeP(['main',5],Global('x'),Number)

class TestRecursionTrans(InferTest):
    iterations=10
    def main():
        global x,y
        x=''
        recursivef()
    def test_y(self):
        #import pdb; pdb.set_trace()
        self.assertTypeP(['main',8],Global('y'), {Number,str})

class TestByteplay(unittest.TestCase):
    def main():
        x=3
    def test(self):
        codeobj=self.main.__code__
        t=ExtraCode.from_code(codeobj)
        u=t.to_code()
        assert codeobj.co_code==u.co_code

# this does not work anymore
#class TestFail0(VerifyTransformation):
#    probabilityOfFail=1
#    vars=['a']
#    @staticmethod
#    def main():
#        global a
#        if randbool(None):
#            a=5
#        else:
#            a='hello'
#        usenum(a)
#        usestr(a)
#    def test_usefn(self):
#        self.assertTypeF(['main',2],Global('usenum'),Callable)
#        self.assertTypeF(['main',2],Global('usestr'),Callable)
#        self.assertTypeP(['main',2],Global('usenum'),Callable)
#        self.assertTypeP(['main',2],Global('usestr'),Callable)
#    def test(self):
#        self.assertTypeF(['main',8],Global('a'),Bot)
#        self.assertTypeF(['main',15],Global('a'),Bot)
#    def testfailedge(self):
#        self.assertFailsOnEntry()

class TestCanFail1(VerifyTransformation):
    probabilityOfFail=0.5
    @staticmethod
    def main():
        global a
        if randbool(None):
            a=5
        usenum(a)
    def test(self):
        self.assertEdge(['main',4],['main',6])
        self.assertTypeF(['main',1],Global('a'),Top)
        self.assertTypeF(['main',3],tos1,Callable)
        self.assertTypeF(['main',2],tos,Callable)
        self.assertTypeF(['main',1],Global('randbool'),Callable)
        self.assertTypeP([],Global('randbool'),Callable)
        self.assertEqual(set(self.analyser.failedges.keys()),{
            (self.getPoint(['main',4]),
            self.getPoint(['main',11]))
            })
    def test2(self):
        self.assertTypeF(['main',11],Global('a'),Number)
        self.assertTypeP(['main',4],Global('a'),Un)
        self.assertEqual(set(self.analyser.failedges.keys()),{
            (self.getPoint(['main',4]),
            self.getPoint(['main',11]))
            })

class TestCanFail2(InferTest):
    @staticmethod
    def main():
        global xyz123
        usenum(xyz123)
    def test(self):
        self.assertFailsOnEntry()

def mayusenum():
    global x
    if randbool(None):
        usenum(x)

class TestMayFail(VerifyTransformation):
    probabilityOfFail=0.5
    vars=['x','a']
    @staticmethod
    def main():
        global x
        x=''
        mayusenum()
        x=5
        mayusenum()

class TestMayFail2(TestMayFail):
    accuracy=1
    def test(self):
        self.assertTypeF(['mayusenum',7],Global('x'),Number)
        self.assertTypeP(['mayusenum',6],Global('x'),{Number,str})


class TestOkArith(VerifyTransformation):
    probabilityOfFail=0

    @staticmethod
    def main():
        global x,y,z
        x=y=45
        z=56
        y+=2

def afun(x,y):
    if x>0:
        xx=x-1
        return afun(xx,y)
    return y

class TestLocals(VerifyTransformation):
    probabilityOfFail=0

    @staticmethod
    def main():
        x='a'
        y='b'
        z=34
        afun(3,6)
        usenum(z)
        usestr(x)
        usestr(y)
    def test(self):
        self.assertTypeF(['main',4],Local('x'),str)

class TestLocals2(VerifyTransformation):
    probabilityOfFail=0

    @staticmethod
    def main():
        x=2
        if abs(x)<4:
            pass

    def test(self):
        self.assertTypeF(['main',6],tos1,Callable)
        self.assertTypeF(['main',5],tos,Callable)
        self.assertTypeF(['main',4],Global('abs'),Callable)
        assert not self.analyser.failedges

def locals3test(x,y):
    if randbool(None):
        return x
    else:
        return y

class VSimpleTest(InferTest):
    @staticmethod
    def main():
        locals3test(3,3)
        locals3test(3,3)
    def test(self):
        self.assertTypeP(['main',10],Global('cadaddr'),Un)
def locals3test(x,y):
    if randbool(None):
        return x
    else:
        return y
class TestLocals3(InferTest):
    @staticmethod
    def main():
        a=locals3test(locals3test('a',None),locals3test(5,True))
    def test(self):
        self.assertTypeP(['main',6],tos1,{str,NoneType})
        self.assertTypeP(['main',10],tos,Number)
        self.assertTypeP(['main',11],Local('a'),{str,Number,NoneType})


def locals4test(x,y):
    if randbool(None):
        return x-y
    return x+y | locals4test(x,y)

class TestLocals4(InferTest):
    @staticmethod
    def main():
        x,y,z=3,3,4
        locals4test(x,locals4test(y,z))
    def test(self):
        self.assertTypeF(['main',3],Global('locals4test'),Callable)
        self.assertTypeF(['main',8],Local('x'),Number)
        self.assertTypeF(['main',8],Local('y'),Number)

def locals5test(x,y):
    return y
class TestLocals5(InferTest):
    @staticmethod
    def main():
        a=locals5test('a',locals5test(5,'a'))
    def test(self):
        self.assertTypeP(['main',10],Local('a'),str)
def locals6test():
    pass
class TestLocals6(InferTest):
    @staticmethod
    def main():
        while randbool(None):
            locals6test()
    def test(self):
        self.assertTypeF(['main',8],Global('locals6test'),Callable)

def bubun():
    global n
    n+=1
class TestSimple(InferTest):
    @staticmethod
    def main():
        bubun()
    def test(self):
        self.assertTypeF(['main',2],Global('n'),Number)
        self.assertTypeF(['main',2,'bubun',1],Global('n'),Number)
        self.assertTypeP(['main',2,'bubun',1],Global('n'),Un)
        self.assertFailsOnEntry()

class TestTrail(InferTest):
    accuracy=1
    @staticmethod
    def main():
        global g
        bubun()
        while randbool(None):
            g=9
            bubun()
        bubun()
    def test(self):
        self.assertTypeP(['main',12],Global('g'),{Un,Number})

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

class TestFixPoint(VerifyTransformation):
    accuracy=3
    probabilityOfFail=0.5
    spotify=staticmethod(lambda a:a)
    @staticmethod
    def main():
        global x1,x2,x3
        x1=x2=x3=None
        fixit()
    def test(self):
        self.analyser.emit(globals())

# global test functions
def recursivef():
    global x,y
    y=x
    x=3
    if randbool():
       recursivef()

def h():
    global x
    x=3

if __name__ == '__main__':
    unittest.main()


