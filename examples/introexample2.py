from sys import argv


def GCDplus(a,b):
    if b==90:
        return GCDplus(10,a)
    elif a!=0:
        return GCDplus(b%a,a)
    else:
        units=input('enter units: ')
        return concat(b,units)

def main():
    if len(argv)<2:
        initial=input('enter initial value: ')
    else:
        initial=argv[1]
    print(initial,"'s largest factor with 90 is",GCDplus(initial, 90))




if __name__=='__main__':
    main()
    #a=Analyser(main,accuracy=4,spotify=lambda a:a)
    #a.printwarnings()
    #a.emit(globals())
    #_main()
