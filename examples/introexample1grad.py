from sys import argv
from gradual import *

@typed
def compute(x1,x2,x3):
    global initial
    if initial%5==0:
        fin=int(input('enter final value: '))
        return x1+x2+x3+fin
    else:
        initial-=1
        return compute(x2,x3,initial)

@typed
def main():
    global initial
    if len(argv)<2:
        initial=abs(input('enter initial value: '))
    else:
        initial=abs(argv[1])
    print('outcome:',compute(None,None,None))

#def main_improved1():
#    global initial
#    if len(argv)<2:
#        initial=abs(int(input('enter initial value: ')))
#    else:
#        initial=abs(int(argv[1]))
#    print('outcome:',compute(None,None,None))
#def main_improved2():
#    global initial
#    if len(argv)<2:
#        initial=abs(int(input('enter initial value: ')))
#    else:
#        initial=abs(int(argv[1]))
#    print('outcome:',compute(0,0,0))


if __name__=='__main__':
    main()
