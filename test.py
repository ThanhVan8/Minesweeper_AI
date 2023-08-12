from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
import heapq
cnf = CNF()


mine = [['1','1','1'],
        ['-','-','2'],
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

#mine=np.array(mine)

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
                        neg = combinations_negative(neighbor_list,len(neighbor_list) - int(InitMatrix[i][j]))
                    
                for clause in pos:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                for clause in neg:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                
                # neighbor_list = []
                # pos = []
                # neg = []
    if [] in cnf.clauses:
        cnf.clauses.remove([])  
    return cnf     

def conflict(mine ,state):
    heuristic = 0
    for clause in cnf.clauses:
        if state in clause or -state in clause:
            continue
        heuristic += 1
    return heuristic

def NewMatrix(mine):
    n = len(mine)
    index_matrix = np.zeros(shape=(n,n))
    #print(index_matrix)
    for i in range(n):
        for j in range(n):
            if mine[i][j] != '-':
                index_matrix[i][j] = int(-(i*n+j+1))
            else:
                index_matrix[i][j] = 0

    return index_matrix.astype(int)

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
            ValueMatrix[row][col] = int(i)
        else: 
            value = abs(i) -1
            row = value // n
            col = value % n
            ValueMatrix[row][col] = int(i)
    
    return ValueMatrix    

def CreateSuccessors(ValueMatrix):
    successors = []
    index = []
    n = len(ValueMatrix)
    #create successors
    for i in range(n):
        for j in range(n):
            if checkIfHaveInfo(ValueMatrix, (i,j)) == True:
                suc1 = ValueMatrix.copy()
                suc2 = ValueMatrix.copy()
                suc1[i][j] = int(i*n+j+1)
                suc2[i][j] = int(-(i*n+j+1))
                successors.append(suc1)
                successors.append(suc2)  
                index.append(i*n+j+1)  
                index.append(-(i*n+j+1))   
    return successors, index 

def AStar(mine, cnf):
    #newmatrix se dc tao tu ma tran ban dau
    InitState = CreateInitState(NewMatrix(mine), singleVars(cnf))
    print(InitState)
    frontier = [(len(cnf.clauses), len(cnf.clauses), 0, InitState)]
    exploredSet = []
    while True:
        f, h, cost, curState = heapq.heappop(frontier)
        
        if h == 0:
            return curState
        
        # exploredSet.append(curState)
        exploredSet.append (curState)
        print(exploredSet[0])

        #xu ly tao successor
        successor, index = CreateSuccessors(curState)
        for i in range (len(successor)):
            for j in range (len(exploredSet)):
                if successor[i].any() != exploredSet[j].any():
                    heapq.heappush(frontier, (conflict(successor[i], index[i]) + cost + 1, conflict(successor[i], index[i]), cost + 1, successor[i]))
        return None
        
        # newmatrix do huy ban tao bang cach chuyen curstate sang newmatrix
        
        
                 
CreateCNF(mine, cnf)     
# print(AStar(mine))  
# singleCNF = singleVars(cnf)
# InitState = CreateInitState(NewMatrix(mine), singleCNF)
# tmp, index = CreateSuccessors(InitState)
# for i in tmp:
#     print(i, type(i))
    
# for i in index:
#     print(i, type(i))
print(AStar(mine, cnf))
#print(NewMatrix(mine))



# with Solver(bootstrap_with=cnf) as solver:
#     # 1.1 call the solver for this formula:
#     print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

#     # 1.2 the formula is satisfiable and so has a model:
#     print('and the model is:', solver.get_model())