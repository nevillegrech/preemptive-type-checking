# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/

# transliterated from Mike Pall's Lua program
# contributed by Mario Pernici
from library import *
from sys import argv,path

try:
  N = int(argv[1])
except:
  N = 100


def main():
  print('start','')
  i = k = ns = 0
  k1 = 1
  d=n=1
  a=t=u=0
  while(True):
    k += 1
    t = n<<1
    n *= k
    a += t
    k1 += 2
    a *= k1
    d *= k1
    if a >= n:
      t=(n*3+a)//d
      u=(n*3+a)%d
      u += n
      if d > u:
        ns = ns*10 + t
        i += 1
        if i % 10 == 0:
          print (ns,i)
          ns = 0
        if i >= N:
          break
        a -= d*t
        a *= 10
        n *= 10

