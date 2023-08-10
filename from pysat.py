from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
cnf = CNF()


mine = [['1','1','1'],
        ['-','-','-'],
        ['-','2','-']]

# mine = [['3','-','-'],
#         ['-','-','-'],
#         ['-','-','-']]

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