# The Computer Language Benchmarks Game

# http://shootout.alioth.debian.org/

#

# contributed by: Olof Kraigher

# 2to3
from sys import argv,path,setrecursionlimit
path.append('..')
setrecursionlimit(40000)
from library import *
from dis import dis
from typer import Analyser

width = 5
height = 10

directions  = { "E" : 0, "NE" : 1, "NW" : 2, "W" : 3, "SW" : 4, "SE" : 5}
rotate      = { "E" : "NE", "NE" : "NW", "NW" : "W", "W" : "SW", "SW" : "SE", "SE" : "E"}
flip        = { "E" : "W", "NE" : "NW", "NW" : "NE", "W" : "E", "SW" : "SE", "SE" : "SW"}
moveE=lambda x,y: (x+1,y)
moveW=lambda x,y: (x-1,y)
moveNE=lambda x,y: (x+(y%2),y-1)
moveNW=lambda x,y: (x+(y%2)-1,y-1)
moveSE=lambda x,y: (x+(y%2),y+1)
moveSW=lambda x,y: (x+(y%2)-1,y+1)

move=dict(E=moveE,W=moveW,NE=moveNE,NW=moveNW,SE=moveSE,SW=moveSW)

pieces =   [    ["E", "E", "E", "SE"],
                ["SE", "SW", "W", "SW"],
                ["W", "W", "SW", "SE"],
                ["E",  "E", "SW", "SE"],
                ["NW", "W", "NW", "SE", "SW"],
                ["E",  "E", "NE", "W"],
                ["NW", "NE", "NE", "W"],
                ["NE", "SE", "E", "NE"],
                ["SE", "SE", "E", "SE"],
                ["E", "NW", "NW", "NW"]]

solutions = []
masks = [0 for i in range(10)]

def valid(x:Number,y:Number)->bool:
    return (0 <= x) and (x < width) and (0 <= y) and (y < height)
legal = lambda mask,board: (mask & board) == 0
def zerocount(mask:Number)->Number:
    return sum([((1<<x) & mask) == 0 for x in range(50)])

def findFreeCell(board):
    y=0
    while y<height:
        x=0
        while x<height:
            if board & (1 << (x + width*y)) == 0:
                return x,y
            x+=1
        y+=1


def floodFill(board, xxx_todo_changeme):
    (x, y) = xxx_todo_changeme
    if not valid(x,y):
        return board
    if board & (1 << (x + width*y)) != 0:
        return board
    board = board | (1 << (x + width*y))

    board = board | floodFill(board, moveE(x,y))
    board = board | floodFill(board, moveW(x,y))
    board = board | floodFill(board, moveNE(x,y))
    board = board | floodFill(board, moveNW(x,y))
    board = board | floodFill(board, moveSE(x,y))
    board = board | floodFill(board, moveSW(x,y))

    return board

def noIslands(mask):
    zeroes = zerocount(mask)

    if zeroes < 5:
        return False

    while mask != 0x3FFFFFFFFFFFF:
        mask = floodFill(mask, findFreeCell(mask))
        new_zeroes = zerocount(mask)

        if zeroes - new_zeroes < 5:
            return False

        zeroes = new_zeroes

    return True

def getBitmask(x:Number,y:Number,piece:MutableSequence) -> tuple:
    mask = (1 << (x + width*y))
    for cell in piece:
        x,y = move[cell](x,y)
        if valid(x,y):
            mask = mask | (1 << (x + width*y))
        else:
            return False, 0

    return True, mask

def allBitmasks(piece, color):
    bitmasks = list(())
    orientations=0
    while orientations < 2:
        last=6 - 3*(color == 4)
        rotations=0
        while rotations<last:
            y=0
            while y<height:
                x=0
                while x<width:
                    isValid, mask = getBitmask(x,y,piece)
                    if isValid and noIslands(mask):
                        append(bitmasks,mask)
                    x+=1
                y+=1
            piece = map(lambda cell: rotate[cell], piece)
            rotations+=1
        piece = map(lambda cell: flip[cell], piece)
        orientations+=1
    return bitmasks

def initMasksAtCell()->MutableSequence:
    return [[[] for j in range(10)] for i in range(width*height)]

def appendMasksAtCell(x:Number,y:Number,z:Number)->NoneType:
    masksAtCell[x][y].append([z])
def generateBitmasks():
    color = 0
    while color<len(pieces):
        piece=lstgetlst(pieces,color)
        masks = allBitmasks(piece, color)
        sort(masks)
        cellMask = 1 << (width*height-1)
        cellCounter = width*height-1

        j = len(masks)-1

        while (j >= 0):
            masksj=lstgetnum(masks,j)
            if (masksj & cellMask) == cellMask:
                appendMasksAtCell(cellCounter,color,masksj)
                j = j-1
            else:
                cellMask = cellMask >> 1
                cellCounter -= 1
        color += 1


def solveCell(cell, board, n):

    global solutions, masks, masksAtCell

    if len(solutions) >= n:
        return

    if board == 0x3FFFFFFFFFFFF:
        # Solved

        s = stringOfMasks(masks)
        append(solutions,s);
        append(solutions,inverse(s));
        return

    if board & (1 << cell) != 0:
        # Cell full

        solveCell(cell-1, board, n)
        return

    if cell < 0:
        # Out of board
        return
    color=0
    while color<10:
        if lstgetnum(masks,color) == 0:
            masks=lstgetlst(lstgetlst(masksAtCell,cell),color)
            mc=0
            while mc<len(masks):
                mask=lstgetnum(masks,mc)
                if legal(mask, board):
                    lstsetnum(masks,color,mask)
                    solveCell(cell-1, board | mask, n)
                    lstsetnum(masks,color,0)
                mc+=1
        color+=1

def solve(n):
    global masksAtCell
    masksAtCell=initMasksAtCell()
    generateBitmasks()
    solveCell(width*height-1, 0, n)


def stringOfMasks(masks):
    s = ""
    mask = 1;
    y=0
    while y<height:
        x=0
        while x<width:
            color=0
            while color<10:
                if (lstgetnum(masks,color) & mask) != 0:
                    s =concat(s,tostr(color))
                    color+=1
                    break
                elif color == 9:
                    s = concat(s,".")
                    color+=1
            x+=1
            mask = mask << 1
        y+=1
    return s

def inverse(s):
    ns = list(s)
    y=0
    while y<height:
        x=0
        while x<width:
            #TODO
            #ns[x + y*width] = s[width-x-1 + (width - y - 1)*width]
            x+=1
        y+=1
    return s

def printSolution(solution):
    y=0
    while y<height:
        x=0
        while x<width:
            printchars(lstgetnum(solution,x + y*width))
            x+=1
        if (y%2) == 0:
            print("",'')
            printchars("")
        else:
            printchars("")
        y+=1

def main():
    solve(6)
    print(len(solutions),"solutions found")
    print('','')
    printSolution(min(solutions))
    print('','')
    printSolution(max(solutions))
    print('','')


if __name__=='__main__':
    a=Analyser(main,accuracy=1)
    a.printwarnings()
    a.emit(globals())
    #_main() # uncomment to run with preemptive type checking
    #main() # uncomment to run (original)


