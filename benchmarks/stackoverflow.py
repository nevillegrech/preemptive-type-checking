# lifted from http://stackoverflow.com/questions/320827/python-type-error-issue
# ported from version 2 to 3.2
import sys
sys.path.append('..')
from typer import Analyser,ExtraCode,Number,NoneType

def oldinput(msg:str) -> Number:
    res=eval(input(msg))
    assert isinstance(res,Number)
    return res

def main():
    status = 1

    print("[b][u]magic[/u][/b]")

    while status == 1:
        print(" ")
        print("would you like to:")
        print(" ")
        print("1) add another spell")
        print("2) end")
        print(" ")
        choice = oldinput("Choose your option: ")
        print(" ")
        if choice == 1:
            name = input("What is the spell called?")
            level = input("What level of the spell are you trying to research?")
            print("What tier is the spell: ")
            print(" ")
            print("1) low")
            print("2) mid")
            print("3) high")
            print(" ")
            tier = oldinput("Choose your option: ")
            if tier == 1:
                materials = 1 + (level * 1)
                rp = 10 + (level * 5)
            elif tier == 2:
                materials = 2 + (level * 1.5)
                rp = 10 + (level * 15)
            elif tier == 3:
                materials = 5 + (level * 2)
                rp = 60 + (level * 40)
            print("research ", name, "to level ", level, "--- material cost = ",  materials, "and research point cost =", rp)
        elif choice == 2:
            status = 0
a=Analyser(main)
a.printwarnings()
a.emit(globals())
_main()
