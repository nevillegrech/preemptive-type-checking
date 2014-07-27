from sys import argv

def compute(x1,x2,x3):
    global initial
    if initial%5==0:
        fin=int(input('enter final value: '))
        return x1+x2+x3+fin
    else:
        initial-=1
        return compute(x2,x3,initial)

def main():
    global initial
    if len(argv)<2:
        initial=abs(int(input('enter initial value: ')))
    else:
        initial=abs(int(argv[1]))
    print('outcome:',compute(None,None,None))

def main34():
    global initial
    if len(argv)<2:
        initial=abs(input('enter initial value: '))
    else:
        initial=abs(argv[1])
    print('outcome:',compute(None,None,None))

def main_improved2():
    global initial
    if len(argv)<2:
        initial=abs(int(input('enter initial value: ')))
    else:
        initial=abs(int(argv[1]))
    print('outcome:',compute(0,0,0))


if __name__=='__main__':
    #main()
    import sys
    sys.path.append('..')
    from library import *
    from typer import *
    from dis import dis
    #main_improved1()
    a=Analyser(main,accuracy=2)
    #a.printwarnings()
    a.emit(globals())
    dis(_main)
    print('===============================================================','')
    print('','')
    dis(main35_compute)
    print('===============================================================','')
    print('','')
    dis(compute34_compute)
    _main()
else:
    from library import *
