from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
cnf = CNF()

# mine = [['1','1','1'],
#         ['-','-','-'],
#         ['-','2','-']]

# mine = [['3','-','-'],
#         ['-','-','-'],
#         ['-','-','-']]

# mine = [['0','-','-'],
#         ['1','-','1'],
#         ['1','-','-']]

# mine = [['-','0','-','0','-','2','-','3','-'],
#         ['0','-','0','-','-','2','-','5','-'],
#         ['-','0','-','-','-','1','2','-','-'],
#         ['0','-','-','-','0','-','1','3','3'],
#         ['-','1','1','1','-','-','-','1','-'],
#         ['0','1','-','1','-','0','-','1','1'],
#         ['0','1','1','1','-','-','-','-','-'],
#         ['2','2','1','-','0','-','1','1','1'],
#         ['-','-','1','-','0','-','1','-','1']]

# mine = [[' ','0',' ','0',' ','2','x','3','-'],
#         ['0',' ','0',' ',' ','2','x','5','-'],
#         [' ','0',' ',' ',' ','1','2','x','x'],
#         ['0',' ',' ',' ','0',' ','1','3','3'],
#         [' ','1','1','1',' ',' ',' ','1','x'],
#         ['0','1','x','1',' ','0',' ','1','1'],
#         ['0','1','1','1',' ',' ',' ',' ',' '],
#         ['2','2','1',' ','0',' ','1','1','1'],
#         ['x','x','1',' ','0',' ','1','x','1']]

# mine = [['0','0','0','0','0','2','-','3','-'],
#         ['0','0','0','0','0','2','-','5','3'],
#         ['0','0','0','0','0','1','2','-','-'],
#         ['0','0','0','0','-','-','1','3','3'],
#         ['0','1','1','1','-','-','-','1','-'],
#         ['-','1','-','1','-','0','-','1','1'],
#         ['-','1','1','1','-','-','-','-','-'],
#         ['2','2','1','-','-','-','1','1','1'],
#         ['-','-','1','-','0','-','1','-','1']]

mine = [['-','1','-','1','-'],
        ['-','2','1','-','-'],
        ['3','-','-','2','2'],
        ['2','-','-','1','-'],
        ['-','1','1','1','1']]

# mine = [[' ','1',' ','1',' '],
#         ['x','2','1',' ','x'],
#         ['3','x',' ','2','2'],
#         ['2','x',' ','1','x'],
#         [' ','1','1','1','1']]

# mine = [['-','-','-','1','-'],
#         ['-','2','1','-','-'],
#         ['3','-','-','-','2'],
#         ['-','-','-','1','-'],
#         ['-','1','1','1','1']]

# mine = [['-','-','-','1','-'],
#         ['x','2','1','x','-'],
#         ['3','-','-','-','2'],
#         ['-','-','-','1','-'],
#         ['-','1','1','1','1']]

mine=np.array(mine)

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

CreateCNF(mine, cnf)       
for clause in cnf.clauses:
    print(clause)

with Solver(bootstrap_with=cnf) as solver:
    # 1.1 call the solver for this formula:
    print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

    # 1.2 the formula is satisfiable and so has a model:
    print('and the model is:', solver.get_model())

# def Astar(mine, cnf):

def resolve(c1, c2):
    clause = []
    n = min(len(c1), len(c2))
    [tmp1, tmp2] = [c1, c2] if n == len(c1) else [c2, c1]
    for v1 in tmp1:
        for v2 in tmp2:
            if v1 == -v2:
                tmp1.remove(v1)
                tmp2.remove(v2)
                tmp1.extend(tmp2)
                clause.extend(list(set(tmp1)))
                break
    for i in range(len(clause)-1):
            if -clause[i] in clause:
                return []
    return clause

def resolution(cnf):
    tmpClause = cnf.clauses.copy()
    singleVars = [tmp[0] for tmp in tmpClause if len(tmp) == 1]

    for i in range(len(tmpClause)-1):
        for j in range(i+1, len(tmpClause)):
            resolvents = resolve(tmpClause[i].copy(), tmpClause[j].copy())
            if len(resolvents)!=0:
                tmpClause.append(resolvents)
            if len(resolvents) == 1:
                if resolvents[0] not in singleVars:
                    singleVars.append(resolvents[0])
                    if -resolvents[0] in singleVars:
                        return []
    
    return singleVars

def singleVars(cnf):
    return [tmp[0] for tmp in cnf.clauses if len(tmp) == 1]

def checkIfHaveInfo(puzzle, cell):
    if puzzle[cell[0]][cell[1]] == 0:
        adjPoint = [-1,0,1]
        for i in adjPoint:
            for j in adjPoint:
                if i == 0 and j == 0:
                    continue
                if 0 <= cell[0]+i < len(puzzle) and 0 <= cell[1]+j < len(puzzle[0]):
                    if puzzle[cell[0]+i][cell[1]+j] != '0':
                        return False
        return True
    return False