from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
cnf = CNF()


mine = [[2,0,0],
        [0,2,0],
        [0,0,0]]

mine=np.array(mine)

def NewMatrix(mine):
    n = len(mine)
    index_matrix = np.array(mine) 
    for i in range(n):
        for j in range(n): 
            index_matrix[i][j] = i*n+j+1
    return index_matrix

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

NumMatrix = NewMatrix(mine)

def is_integer_list(lst):
    if not isinstance(lst, list):
        return False
    
    for item in lst:
        if not isinstance(item, int):
            return False
    
    return True
def convert_to_integer_list(clauses):
    integer_clauses = []
    
    for clause in clauses:
        integer_clause = [int(literal) for literal in clause]
        integer_clauses.append(integer_clause)
    
    return integer_clauses
def CreateCNF(InitMatrix, NumMatrix, cnf):
    pos = []
    neg = []
    neighbor_list = []
    for i in range(len(InitMatrix)):
        for j in range(len(InitMatrix[i])):
            if  InitMatrix[i][j] > 0:
                tmp = InitMatrix[i][j]
                neighbors = [(i+1, j), 
                            (i, j+1), 
                            (i-1, j), 
                            (i, j-1), 
                            (i+1, j+1), 
                            (i+1, j-1), 
                            (i-1, j+1), 
                            (i-1, j-1)]
                for neighbor in neighbors:
                    #check exist
                    if(0 <= neighbor[0] < len(InitMatrix)) and (0 <= neighbor[1] < len(InitMatrix[i])):
                        if(InitMatrix[neighbor[0]][neighbor[1]] == 0):
                            neighbor_list.append(NumMatrix[neighbor[0]][neighbor[1]])

                #positive num (having bomb)
                pos = combinations_positive(neighbor_list,len(neighbor_list)-InitMatrix[i][j] + 1)
                #negative num (not having bomb)
                if len(neighbor_list) - InitMatrix[i][j] != 1:
                    neg = combinations_negative(neighbor_list,len(neighbor_list) - InitMatrix[i][j])
                
                for clause in pos:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                for clause in neg:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                
                neighbor_list = []
                pos = []
                neg = []
    cnf.clauses.remove([])  
    return cnf     


    
CreateCNF(mine, NumMatrix, cnf)       
for clause in cnf.clauses:
    print(clause)
    
    
with Solver(bootstrap_with=cnf) as solver:
    # 1.1 call the solver for this formula:
    print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

    # 1.2 the formula is satisfiable and so has a model:
    print('and the model is:', solver.get_model())

    # 2.1 apply the MiniSat-like assumption interface:
    print('formula is',
        f'{"s" if solver.solve(assumptions=[1, 2]) else "uns"}atisfiable',
        'assuming x1 and x2')

    # 2.2 the formula is unsatisfiable,
    # i.e. an unsatisfiable core can be extracted:
    print('and the unsatisfiable core is:', solver.get_core())