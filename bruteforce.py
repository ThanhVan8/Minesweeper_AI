from pysat.formula import CNF
import time, tracemalloc

cnf = CNF()

# mine = [['1','1','1'],
#         ['-','-','2'],
#         ['-','2','-']]

mine = [[' ','0',' ','0',' ','2','x','3','-'],
        ['0',' ','0',' ',' ','2','x','5','-'],
        [' ','0',' ',' ',' ','1','2','x','x'],
        ['0',' ',' ',' ','0',' ','1','3','3'],
        [' ','1','1','1',' ',' ',' ','1','x'],
        ['0','1','x','1',' ','0',' ','1','1'],
        ['0','1','1','1',' ',' ',' ',' ',' '],
        ['2','2','1',' ','0',' ','1','1','1'],
        ['x','x','1',' ','0',' ','1','x','1']]

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

def singleVars(cnf):
    return [tmp[0] for tmp in cnf.clauses if len(tmp) == 1]

def checkExist(assignedList, clause):
    for i in clause:
        if i in assignedList:
            return True
    return False

def checkConflict(assignedList):    
    for clause in cnf.clauses:
        if checkExist(assignedList, clause) == False:
            return False
    return True

def BruteforceSolver(mine):
    singleCNFs = singleVars(cnf)
    numCell = len(mine) * len(mine[0])
    notAssigned = []
    for cell in range(1, numCell+1):    # from 1 to numCell
        if cell not in singleCNFs and -cell not in singleCNFs and (any(cell in clause for clause in cnf.clauses) or any(cell in clause for clause in cnf.clauses)):
            notAssigned.append(cell)

    assigned = singleCNFs.copy()
    
    maxRange = 2 ** len(notAssigned)
    res = []
    for i in range(maxRange):
        suc = []
        for j in range(len(notAssigned)):
            bit = (i >> j) & 1  # Lấy giá trị bit thứ j của số i
            value = -1 if bit == 0 else 1
            suc.append(value * notAssigned[j])
        res.append(suc) 
        
    for i in res:
        tmp = assigned.copy()
        for j in i:
            tmp.append(j)
        if checkConflict(tmp):
            return tmp
        

def Display(resList):
    State = [row[:] for row in mine]
    for i in range(len(State)):
        for j in range(len(State[0])):
            idx = i*len(mine) +j+1
            if idx in resList:
                State[i][j] = idx
            elif -idx in resList:
                State[i][j] = -idx
            else:
                State[i][j] = 0

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
Output = BruteforceSolver(mine)
tracemalloc.stop()
t = (time.time() - startTime)


Display(Output)

print()
print(f"Running time: {t * 1000:.4f} ms")