from pysat.formula import CNF
from pysat.solvers import Solver
import heapq
import time, tracemalloc

cnf = CNF()

# mine = [['1','1','1'],
#         ['-','-','-'],
#         ['-','2','-']]

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

mine = [['-','1','-','2','2','-','1','-','-'],
        ['-','1','1','2','-','2','1','1','1'],
        ['1','1','-','1','1','1','-','1','-'],
        ['-','1','-','-','-','-','1','2','2'],
        ['1','2','1','1','1','1','2','-','1'],
        ['-','1','-','1','1','-','2','1','1'],
        ['-','1','1','1','1','1','1','-','-'],
        ['1','1','-','-','-','1','-','1','-'],
        ['-','1','0','-','-','1','-','1','-']]

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
            if i in state:
                return True
    return False

def conflict(state):
    heuristic = 0
    for clause in cnf.clauses:
        if checkExist(state, clause) == False:
            heuristic += 1
    return heuristic

def checkIfHaveInfo(cell):
    if any(cell in clause for clause in cnf.clauses) or any(cell in clause for clause in cnf.clauses):
        return True
    return False

def singleVars(cnf):
    return [tmp[0] for tmp in cnf.clauses if len(tmp) == 1]

def CreateInitState(mine):
    singleCNFs = singleVars(cnf)
    numCell = len(mine) * len(mine[0])
    state = []
    for cell in range(1, numCell+1):    # from 1 to numCell
        if cell in singleCNFs:
            state.append(cell)
        elif -cell in singleCNFs:
            state.append(-cell)
        else:
            state.append(0)
    return state

def CreateSuccessors(state):
    successors = []
    numCell = len(mine) * len(mine[0])
    for i in range(numCell):
        if state[i] == 0 and checkIfHaveInfo(i + 1):
            suc1 = [tmp for tmp in state]
            suc2 = [tmp for tmp in state]
            suc1[i] = i+1
            suc2[i] = -i-1
            successors.append(suc1)
            successors.append(suc2)
    return successors

def AStar(mine):
    startstate = CreateInitState(mine)
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
            if i not in exploredSet and i not in [state for _, _, _, state in frontier]:
                heapq.heappush(frontier, (conflict(i) + cost + 1, conflict(i), cost + 1, i))
    return None

def Display(resList):
    State = [row[:] for row in mine]
    for i in range(len(State)):
        for j in range(len(State[0])):
            idx = i*len(mine) + j
            State[i][j] = resList[idx]

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

print()
print(f"Running time: {t * 1000:.4f} ms")