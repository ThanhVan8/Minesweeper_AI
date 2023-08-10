from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
cnf = CNF()


mine = [[3,0,0],
        [0,0,0],
        [0,0,0]]

mine=np.array(mine)

#create number matrix
def NewMatrix(mine):
    n = len(mine)
    index_matrix = np.array(mine) 
    for i in range(n):
        for j in range(n): 
            index_matrix[i][j] = i*n+j+1
    return index_matrix

#recursion to find bomb clause
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


#recursion to find not bomb clause
def combinations_negative(ValueList, k):
    if k == 0:
        return [[]]
    if not ValueList:
        return []

    result = []
    first, rest = ValueList[0], ValueList[1:]
    #recursive with rest digits
    for combo in combinations_negative(rest, k - 1):
        result.append([-first] + combo)  # change opposite
    result.extend(combinations_negative(rest, k))
    return result


def CreateCNF(InitMatrix, NumMatrix, cnf):
    pos = []
    neg = []
    neighbor_list = []
    for i in range(len(InitMatrix)):
        for j in range(len(InitMatrix[i])):
            if  InitMatrix[i][j] > 0:
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
                            neighbor_list.append(NumMatrix[neighbor[0]][neighbor[1]]) #append neighbor position

                #positive num (having bomb)
                pos = combinations_positive(neighbor_list,len(neighbor_list)-InitMatrix[i][j] + 1)
                #negative num (not having bomb)
                if len(neighbor_list) - InitMatrix[i][j] != 1:
                    neg = combinations_negative(neighbor_list,len(neighbor_list) - InitMatrix[i][j])
                
                #append bomb clause to CNF
                for clause in pos:
                    clause = [int(literal) for literal in clause] #convert integer list
                    if clause not in cnf.clauses: #check exist
                        cnf.append(clause)
                        
                #append not bomb clause to CNF        
                for clause in neg:
                    clause = [int(literal) for literal in clause] #convert integer list
                    if clause not in cnf.clauses:#check exist
                        cnf.append(clause)
                
                neighbor_list = []
                pos = []
                neg = []
    #check exist a null list and remove that            
    if [] in cnf.clauses:
        cnf.clauses.remove([])
    return cnf     


NumMatrix = NewMatrix(mine) #position matrix
CreateCNF(mine, NumMatrix, cnf)       

for clause in cnf.clauses:
    print (clause)

    
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