from pysat.formula import CNF
from pysat.solvers import Solver
cnf = CNF()
import numpy as np

# mine = [['-','-','0'],
#         ['-','-','-'],
#         ['1','-','-']]

mine = [['1','1','1'],
        ['-','-','2'],
        ['-','2','-']]

# mine = [['3','-','-'],
#         ['-','-','-'],
#         ['-','-','-']]

# mine = [['0','-','-'],
#         ['-','-','-'],
#         ['-','1','-']]

# mine = [['-','-','-'],
#         ['-','-','-'],
#         ['-','2','-']]

def combinations_positive(ValueList, k):
    if k == 0:
        return [[]]
    if not ValueList:
        return []

    result = []
    first, rest = ValueList[0], ValueList[1:]
    for combo in combinations_positive(rest, k - 1):
        result.append([first] + combo)
    result.extend(combinations_positive(rest, k))
    return result

def combinations_negative(ValueList, k):
    if k == 0:
        return [[]]
    if not ValueList:
        return []

    result = []
    first, rest = ValueList[0], ValueList[1:]
    for combo in combinations_negative(rest, k - 1):
        result.append([-first] + combo)  # Đổi dấu cho phần tử đầu tiên
    result.extend(combinations_negative(rest, k))
    return result

def neighbors(puzzle, cell):
    res = []
    adjPoint = [-1,0,1]
    nCol = len(puzzle[0])
    for i in adjPoint:
        for j in adjPoint:
            if i == 0 and j == 0:
                continue
            if 0 <= cell[0]+i < len(puzzle) and 0 <= cell[1]+j < len(puzzle[0]):
                if puzzle[cell[0]+i][cell[1]+j].isnumeric() is False:
                    res.append((cell[0]+i)*nCol +cell[1]+j +1)
    return res

def CreateCNF(InitMatrix, cnf):
    pos = []
    neg = []
    neighbor_list = []
    
    for i in range(len(InitMatrix)):
        for j in range(len(InitMatrix[i])):
            if  InitMatrix[i][j].isnumeric():
                simple = [-(i*len(InitMatrix) +j +1)]
                cnf.append(simple)
                neighbor_list = neighbors(InitMatrix, (i, j))
                if int(InitMatrix[i][j]) == 0:
                    neg = combinations_negative(neighbor_list,1)
                elif int(InitMatrix[i][j]) == len(neighbor_list):
                    pos = combinations_positive(neighbor_list,1)
                else:
                    #positive num (having bomb)
                    pos = combinations_positive(neighbor_list,len(neighbor_list)-int(InitMatrix[i][j]) + 1)
                    #negative num (not having bomb)
                    if len(neighbor_list) - int(InitMatrix[i][j]) != 1:
                        neg = combinations_negative(neighbor_list,int(InitMatrix[i][j])+1)
                    
                for clause in pos:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                        # myPos.append(clause)
                for clause in neg:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                        # myNeg.append(clause)
                
    if [] in cnf.clauses:
        cnf.clauses.remove([])  
    return cnf     

# lấy các CNF True
def preHandle(cnf):
    myPos = []
    for clause in cnf:
        if(clause[0]>0): 
            myPos.append(clause)
    return myPos 
            
def isConflict(mineList):
    tmp = mine.copy()
    x = len(mine)
    # gán bom vào ma trận
    for i in mineList:
        # dòng 1
        if(i<=x):
            tmp[0][i-1] = 'X'
        else:   # các dòng còn lại
            row = int((i-1)/x)
            col = i - row*x -1
            tmp[row][col] = 'X'
            
    for i in range(len(tmp)):
        for j in range(len(tmp[i])):
            if(tmp[i][j].isnumeric()):
                neighbor_list = neighbors(tmp, (i, j))
                count = 0
                for k in neighbor_list:
                    if(k in mineList):
                        count+=1
                        # số bom không hợp lệ
                        if(count > int(tmp[i][j])):
                            return False
    return True

            
def bruteForce(cnf):

    myPos = preHandle(cnf)
    tmpPos = myPos.copy()   
    first = myPos.pop(0)
    
    for i in first:
        mineList = []
        index = [i]
        while(True):
            nextStep = []
            mineList.append(index[0])             
            for bomb in mineList:
                tmp = []
                for j in tmpPos:
                    if(bomb not in j):
                        tmp.append(j)
                tmpPos = tmp.copy()
            if(len(tmpPos)!=0):
                nextStep.append(tmpPos[0])
                index = nextStep[-1].copy()
                            
            if(len(tmpPos) == 0):
                # kiểm tra kết quả
                if(isConflict(mineList) and mineList):
                    return mineList

                tmpPos = myPos.copy()   
                mineList.pop(-1)   
                index.pop(0)
                if(len(index) == 0):
                    break
    return None

def NewMatrix(mine):
    n = len(mine)
    index_matrix = []
    for i in range (n):
        index_matrix.append([0 for j in range(len(mine[i]))])

    for i in range(n):
        for j in range(n):
            if mine[i][j] != '-':
                index_matrix[i][j] = -int((i*n+j+1))
            else:
                index_matrix[i][j] = 0
    return index_matrix

def Display(State):
    #tien xu ly
    tmp = [row[:] for row in NewMatrix(mine)]
    for i in range(len(tmp)):
        for j in range(len(tmp[0])):
            if i*len(mine)+j+1 in State:
                tmp[i][j] = i*len(mine)+j+1
    # xu ly output
    output = [row[:] for row in tmp]
    adjPoint = [-1, 0 , 1]
    for i in range(len(tmp)):
        for j in range(len(tmp[0])):
            if tmp[i][j] > 0: # kiem tra o bom
                output[i][j] = 'X'
            elif tmp[i][j] < 0:
                cnt = 0
                for k in adjPoint:
                    for l in adjPoint:
                        if 0 <= i+k < len(tmp) and 0 <= j+l < len(tmp[0]):
                            if tmp[i + k][j + l] > 0 :
                                cnt += 1
                output[i][j] = cnt
            elif tmp[i][j] == 0:
                output[i][j] = '-'
            
    for i in range(len(output)):
        print()
        for j in range(len(output[0])):
            print(output[i][j], end=' ')

CreateCNF(mine, cnf)    
Display(bruteForce(cnf))
