from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
import heapq
import random, time, tracemalloc

cnf = CNF()

mine = [['1','1','1'],
        ['-','-','-'],
        ['-','2','-']]

# mine = [['-','-','-','1','-'],
#         ['-','2','1','-','-'],
#         ['3','-','-','-','2'],
#         ['-','-','-','1','-'],
#         ['-','1','1','1','1']]

# mine = [['3','-','-'],
#         ['-','-','-'],
#         ['-','-','-']]

# mine = [['0','-','-'],
#         ['1','-','1'],
#         ['1','-','-']]

# mine=np.array(mine)

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
                for clause in neg:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                
    if [] in cnf.clauses:
        cnf.clauses.remove([])  
    return cnf     

def checkExist(state, clause):
    for i in clause:
        for j in state:
            if int(i) in j:
                return True
    return False
def conflict(state):
    heuristic = 0
    
    for clause in cnf.clauses:
        if checkExist(state, clause) == False:
            heuristic += 1
            
    return heuristic

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

def checkIfHaveInfo(puzzle, cell):
    if puzzle[cell[0]][cell[1]] == 0:
        adjPoint = [-1,0,1]
        for i in adjPoint:
            for j in adjPoint:
                if i == 0 and j == 0:
                    continue
                if 0 <= cell[0]+i < len(puzzle) and 0 <= cell[1]+j < len(puzzle[0]):
                    if puzzle[cell[0]+i][cell[1]+j] != 0:
                        return True
        return False
    return False

def singleVars(cnf):
    return [tmp[0] for tmp in cnf.clauses if len(tmp) == 1]

def CreateInitState(ValueMatrix, Simply_List):
    n = len(ValueMatrix)
    #use single CNF to create InitState
    for i in Simply_List:
        if i > 0:
            value = i -1
            row = value // n
            col = value % n
            ValueMatrix[row][col] = i
        else: 
            value = abs(i) -1
            row = value // n
            col = value % n
            ValueMatrix[row][col] = i
    
    return ValueMatrix       

def CreateSuccessors(InitMatrix):
    
    successors = []
    n = len(InitMatrix)
    #create successors
    for i in range(n):
        for j in range(n):
            if checkIfHaveInfo(InitMatrix, (i,j)) == True:
                #print(tmp)
                
                suc1 = [row[:] for row in InitMatrix]
                suc2 = [row[:] for row in InitMatrix]
          
                value1 = int(i*n+j+1)
                value2 = int(-(i*n+j+1))
          
                suc1[i][j] = value1
                suc2[i][j] = value2
                
                successors.append(suc1)
                successors.append(suc2)
                
               
    return successors

def AStar(mine):
    singleCNF = singleVars(cnf)
    startstate = CreateInitState(NewMatrix(mine), singleCNF)
    frontier = [(conflict(startstate), conflict(startstate), 0, startstate)]
    exploredSet = []
    while True:
        f, h, cost, curState = heapq.heappop(frontier)
        if h == 0:
            return curState
        
        exploredSet.append(curState)
        
        #xu ly tao successor
        successor = CreateSuccessors(curState)
        
        for i in successor:
            if i not in exploredSet:
                heapq.heappush(frontier, (conflict(i) + cost + 1, conflict(i), cost + 1, i))
    return None
            
 
def Display(State):
    output = [row[:] for row in State]
    adjPoint = [-1, 0 , 1]
    for i in range(len(State)):
        for j in range(len(State[0])):
            if State[i][j] > 0: # kiem tra o bom
                output[i][j] = 'X'
            elif State[i][j] < 0:
                cnt = 0
                for k in adjPoint:
                    for l in adjPoint:
                        if 0 <= i+k < len(State) and 0 <= j+l < len(State[0]):
                            if State[i + k][j + l] > 0 :
                                cnt += 1
                output[i][j] = cnt
            elif State[i][j] == 0:
                output[i][j] = '-'
            
    for i in range(len(output)):
        print()
        for j in range(len(output[0])):
            print(output[i][j], end=' ')

CreateCNF(mine, cnf)
for clause in cnf.clauses:
    print(clause)    



tracemalloc.start()
startTime = time.time()
Output = AStar(mine)
tracemalloc.stop()
t = (time.time() - startTime)

Display(Output) 
# print(Output)
print()
print(f"Running time: {t * 1000:.4f} ms")


# with Solver(bootstrap_with=cnf) as solver:
#     # 1.1 call the solver for this formula:
#     print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

#     # 1.2 the formula is satisfiable and so has a model:
#     print('and the model is:', solver.get_model())
