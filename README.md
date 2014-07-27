preemptive-type-checking
========================
This repository contains a preemptive type checking implementation
for a subset of the cpython 3.3, Python programming language
implementation.

What is preemptive type checking?
---------------------------------
This is a novel type checking mechanism, based on years of research at
the University of Southampton. At the core of this mechanism is a type
inference system that identifies potential type errors through a flow-
sensitive static analysis. This analysis is invoked at a very late stage,
after the compilation to bytecode and initialisation of the program.
It computes for every expression the variable's present (from the values
that it has last been assigned) and future (with which it is used in
the further program execution) types, respectively. Using this
information, our mechanism inserts type checks at strategic points
in the original program, thus preemptive type errors at an early stage.

Usage
-----
Simply import the library into your program, to start using preemptive
type checking, instead of dynamic typing, as follows:

```python
from typer import Analyser

def main():
    # Python, with some restricted features
    .

if __name__=='__main__':
    # Full Python language up to here.
    # We first analyse the function initialised above.
    a=Analyser(main)
    # We transform the function such that it 
    # implements preemptive type checking semantics.
    a.emit()
    # We call the transformed function.
    _main()
```

About
-----
Written by: Neville Grech

For more information about preemptive type checking read my [PhD thesis](http://eprints.soton.ac.uk/361277/8.hasCoversheetVersion/__soton.ac.uk_ude_PersonalFiles_Users_slb1_mydocuments_grech.pdf "Neville Grech - Preemptive Type Checking")

If you would like to contact me, email me at nevillegrech at gmail.

