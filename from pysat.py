from pysat.formula import CNF
from pysat.solvers import Solver
# Khởi tạo một công thức CNF trống
import numpy as np
# cnf = CNF(from_clauses=[])
cnf = CNF()

mine = [[2,0,0],
        [0,2,0],
        [0,0,0]]

mine=np.array(mine)

def NewMatrix(mine):
    n = len(mine)
    print(n)
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
#def CreateNeighbors(IndexPosition):


cnf_list = []
IndexMatrix = NewMatrix(mine)
neighbors =[]
neighbor_list = list()
pos = []
neg = []
for i in range(len(mine)):
    for j in range(len(mine[i])):
        if  mine[i][j] > 0:
            tmp = mine[i][j]
            neighbors = [(i+1, j), 
                        (i, j+1), 
                        (i-1, j), 
                        (i, j-1), 
                        (i+1, j+1), 
                        (i+1, j-1), 
                        (i-1, j+1), 
                        (i-1, j-1),]
            nei_list = list()
            for neighbor in neighbors:
                #check exist
                if(0 <= neighbor[0] < len(mine)) and (0 <= neighbor[1] < len(mine[i])):
                    if(mine[neighbor[0]][neighbor[1]] == 0):
                        nei_list.append(IndexMatrix[neighbor[0]][neighbor[1]])

            pos = combinations_positive(nei_list,len(nei_list)-mine[i][j] + 1)
            #print(len(nei_list), mine[i][j])   
            if len(nei_list) - mine[i][j] != 1:
                neg = combinations_negative(nei_list,len(nei_list) - mine[i][j])
            
            for index in pos:
                #print(index)
                if index not in cnf.clauses:
                    cnf.append(index)   
            for index in neg:
                #print(index)
                if index not in cnf.clauses:
                    cnf.append(index)
            nei_list = []
            pos = []
            neg = []
            #print() 
cnf.clauses.remove([])              
# for clause in cnf.clauses:
#     print(clause)
print(cnf.clauses)
    
with Solver(bootstrap_with=cnf.clauses) as solver:
    # 1.1 call the solver for this formula:
    print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

    # 1.2 the formula is satisfiable and so has a model:
    print('and the model is:', solver.get_model())

    # # 2.1 apply the MiniSat-like assumption interface:
    # print('formula is',
    #     f'{"s" if solver.solve(assumptions=[1, 2]) else "uns"}atisfiable',
    #     'assuming x1 and x2')

    # # 2.2 the formula is unsatisfiable,
    # # i.e. an unsatisfiable core can be extracted:
    # print('and the unsatisfiable core is:', solver.get_core())