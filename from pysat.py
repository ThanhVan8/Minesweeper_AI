from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
import heapq
cnf = CNF()

mine = [['0','1','1'],
        ['-','-','-'],
       ['-','2','-']]




#mine = [['-','1','-','1','-'],
#        ['-','2','1','-','-'],
#        ['3','-','-','2','2'],
#        ['2','-','-','1','-'],
#        ['-','1','1','1','1']]

#recursion to find bomb clause 
#mine = [['','0','0','0','0','2','-','3','-'],
#        ['0','0','0','0','0','2','-','5','3'],
#        ['0','0','0','0','0','1','2','-','-'],
#        ['0','0','0','0','-','-','1','3','3'],
#        ['','1','1','1','-','-','-','1','-'],
#        ['-','1','-','1','-','0','-','1','1'],
#        ['-','1','1','1','-','-','-','-','-'],
#        ['2','2','1','-','-','-','1','1','1'],
#        ['-','-','1','-','0','-','1','-','1']]
#mine = [[0,'-','-'],
#         [1,'-',1],
 #        [1,'-','-']]

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


#recursion to find not bomb clause
def combinations_negative(ValueList, k):
    result = []
    if k == 0:
        return [[]]
    if not ValueList:
        return []
    
 
    first, rest = ValueList[0], ValueList[1:]
    #recursive with rest digits
    for combo in combinations_negative(rest, k - 1):
        result.append([-first] + combo)  # change opposite
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

                #checking CNF
                if int(InitMatrix[i][j]) == 0: #check value = 0
                    neg = combinations_negative(neighbor_list, 1)
                    
                elif len(neighbor_list) == int(InitMatrix[i][j]): #number neighbors = number bomb
                    pos = combinations_positive(neighbor_list, 1)
                    
                else:
                    pos = combinations_positive(neighbor_list,len(neighbor_list)-int(InitMatrix[i][j]) + 1)
                    if len(neighbor_list) - int(InitMatrix[i][j]) != 1:
                        neg = combinations_negative(neighbor_list,len(neighbor_list) - int(InitMatrix[i][j]))
                
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

    # 2.1 apply the MiniSat-like assumption interface:
    print('formula is',
        f'{"s" if solver.solve(assumptions=[1, 2]) else "uns"}atisfiable',
        'assuming x1 and x2')

    # 2.2 the formula is unsatisfiable,
    # i.e. an unsatisfiable core can be extracted:
    print('and the unsatisfiable core is:', solver.get_core())
    
def NewMatrix(mine):
    n = len(mine)
    index_matrix = []
    for i in range (n):
        index_matrix.append([0 for j in range(len(mine[i]))])

    for i in range(n):
        for j in range(n):
            if mine[i][j] != '-':
                index_matrix[i][j] = -(i*n+j+1)
            else:
                index_matrix[i][j] = 0
    return index_matrix


ValueMatrix = NewMatrix(mine)   

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
    #print(tmp[2][1])
    #create successors
    for i in range(n):
        for j in range(n):
            if checkIfHaveInfo(InitMatrix, (i,j)) == True:
                #print(tmp)
                
                suc1 = [row[:] for row in InitMatrix]
                suc2 = [row[:] for row in InitMatrix]
                print(suc1)
                print(suc2)
                value1 = int(i*n+j+1)
                value2 = int(-(i*n+j+1))
                print(value1)
                print(value2)
                suc1[i][j] = value1
                suc2[i][j] = value2
                print(suc1)  
                print(suc2)  
                #print(InitMatrix)
                successors.append(suc1)
                successors.append(suc2)
                print()  
               
    return successors   
     

singleCNF = singleVars(cnf)
InitState = CreateInitState(ValueMatrix, singleCNF)
tmp = CreateSuccessors(InitState)
