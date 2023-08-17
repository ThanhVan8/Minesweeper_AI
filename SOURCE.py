from pysat.formula import CNF
from pysat.solvers import Solver
import time, tracemalloc
import heapq


#Read Input File
def ReadInput():
    data = []
    n = input("enter number from 1 to 5: ")
    f = open("input" + str(n) +'.txt')
    for line in f: #Read every line
        line = line.strip()  
        row = line.split()   
        data.append(row)   
    
    return data, n

# Two types of combinations
def combinations_positive(ValueList, k): #full positive
    if k == 0:
        return [[]]
    if not ValueList:
        return []

    result = []
    first, rest = ValueList[0], ValueList[1:]
    for combo in combinations_positive(rest, k - 1): #recursive positive 
        result.append([first] + combo)
    result.extend(combinations_positive(rest, k))
    return result

def combinations_negative(ValueList, k): #full negative
    if k == 0:
        return [[]]
    if not ValueList:
        return []

    result = []
    first, rest = ValueList[0], ValueList[1:]
    for combo in combinations_negative(rest, k - 1): #recursive negative
        result.append([-first] + combo)  # change assigned
    result.extend(combinations_negative(rest, k))
    return result

# Get all neighbors for every position
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

#Create List of CNF Clauses
def CreateCNF(InitMatrix, cnf):
    pos = []
    neg = []
    neighbor_list = []
    
    for i in range(len(InitMatrix)):
        for j in range(len(InitMatrix[i])):
            if  InitMatrix[i][j].isnumeric(): #if a position is number
                simple = [-(i*len(InitMatrix) +j +1)] #change the number to the value of CNF clause
                cnf.append(simple)
                neighbor_list = neighbors(InitMatrix, (i, j))
                
                #three types of creates CNF clauses
                if int(InitMatrix[i][j]) == 0: # value = 0 -> only get negative combination
                    neg = combinations_negative(neighbor_list,1) 
                    
                elif int(InitMatrix[i][j]) == len(neighbor_list):# value = number of neighbors -> only get positive combination
                    pos = combinations_positive(neighbor_list,1)
                    
                else: # using formula to calculate
                    #positive num (having bomb)
                    pos = combinations_positive(neighbor_list,len(neighbor_list)-int(InitMatrix[i][j]) + 1)
                    #negative num (not having bomb)
                    if len(neighbor_list) - int(InitMatrix[i][j]) != 1:
                        neg = combinations_negative(neighbor_list,int(InitMatrix[i][j])+1)
                    
                #append CNFs
                for clause in pos:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                        
                for clause in neg:
                    clause = [int(literal) for literal in clause]
                    if clause not in cnf.clauses:
                        cnf.append(clause)
                
    if [] in cnf.clauses: #delete null CNF clause
        cnf.clauses.remove([])  
    return cnf  


#below function are used for AStar
#Check if the clause's attributes exist in the state
def checkExist(state, clause):
    for i in clause:
        if i in state:
            return True #if exist
    return False #if not

#Calculate heuristics
def conflict(state):
    heuristic = 0
    for clause in cnf.clauses:
        if checkExist(state, clause) == False:
            heuristic += 1
    return heuristic

#checking if cell appears in any clause of CNF (means that cell has information)
def checkIfHaveInfo(cell): 
    if any(cell in clause for clause in cnf.clauses) or any(cell in clause for clause in cnf.clauses):
        return True
    return False

#get single CNF clause
def singleVars(cnf):
    return [tmp[0] for tmp in cnf.clauses if len(tmp) == 1]

#Create Init State for A*
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

#Create Successors from a state
def CreateSuccessors(state):
    successors = []
    numCell = len(mine) * len(mine[0])
    for i in range(numCell):
        if state[i] == 0 and checkIfHaveInfo(i + 1): #if cell is not assigned and has information
            suc1 = [tmp for tmp in state]
            suc2 = [tmp for tmp in state]
            suc1[i] = i+1 #positive
            suc2[i] = -i-1 #negative
            successors.append(suc1)
            successors.append(suc2)
    return successors

#A* algorithm
def AStar(mine):
    startstate = CreateInitState(mine)
    frontier = [(conflict(startstate), conflict(startstate), 0, startstate)]
    exploredSet = []
    cnt = 0
    while cnt < 10000: #max Step = 10000
        f, h, cost, curState = heapq.heappop(frontier)
        if h == 0:
            return curState
        
        exploredSet.append(curState)
        
        #Create successors
        successor = CreateSuccessors(curState)
        
        for i in successor:
            if i not in exploredSet and i not in [state for _, _, _, state in frontier]:
                heapq.heappush(frontier, (conflict(i) + cost + 1, conflict(i), cost + 1, i))
    return None

#for Backtracking
#check conflict to stop
def checkConflict(assignedList):    
    for clause in cnf.clauses:
        if checkExist(assignedList, clause) == False:   # if there is a clause that is not satisfied by the assignment
            return False
    return True

#Backtracking algorithm
def backtrackingSolver():
    singleCNFs = singleVars(cnf)    # get clause with only one literal
    numCell = len(mine) * len(mine[0])  # number of cells
    notAssigned = []    # init list of cells that are not assigned
    for cell in range(1, numCell+1):    # from 1 to numCell
        if cell not in singleCNFs and -cell not in singleCNFs and (any(cell in clause for clause in cnf.clauses) or any(cell in clause for clause in cnf.clauses)):
            notAssigned.append(cell)

    assigned = singleCNFs.copy()    # init list of cells that are assigned
    val = [1, -1]   # possible values for each cell (1: bomb, -1: no bomb)

    def backtracking(assigned, idx=0):  # idx: current index of notAssigned
        if idx == len(notAssigned): # if all cells are assigned
            return checkConflict(assigned)
        
        for bomb in val:
            notAssigned[idx] *= bomb
            assigned.append(notAssigned[idx])
            res = backtracking(assigned, idx + 1)   # go to next cell need to be assigned
            if res:
                return True
            else:
                assigned.pop(-1) # pop out the latest assigned value
        return False
    
    if backtracking(assigned):
        return assigned
    else:
        return None


# for BF
# get posiclause in CNF 
def preHandle(cnf):
    myPos = []
    for clause in cnf:
        if(clause[0]>0): 
            myPos.append(clause)
    return myPos 
            
# check conflit on matrix
def isConflict(mineList):
    tmp = mine.copy()
    x = len(mine)
    
    # assign bombs into correspinding cells 
    for i in mineList:
        # for cells in line 1
        if(i<=x):
            tmp[0][i-1] = 'X'
        else:   # the other cells 
            row = int((i-1)/x)
            col = i - row*x -1
            tmp[row][col] = 'X'
            
    # check conflict by counting the number of bomb around a positive number in matrix 
    for i in range(len(tmp)):
        for j in range(len(tmp[i])):
            if(tmp[i][j].isnumeric()):
                # get index of neighbor list
                neighbor_list = neighbors(tmp, (i, j))
                count = 0
                # count number of bombs in neighbor list to check the validation 
                for k in neighbor_list:
                    if(k in mineList):
                        count+=1
                        # the quantity of bombs is invalid 
                        if(count > int(tmp[i][j])):
                            return True
    return False
          
def BruteForce(cnf):

    # pre-handle for cnf to get positive clauses in it
    myPos = preHandle(cnf)
    # a temporary list of positive clauses
    tmpPos = myPos.copy()   
    first = myPos.pop(0)
    
    # get the first clause to make the loop (at leats 1 value in 'firt' is true - has bomb)
    for i in first:
        mineList = []
        
        # index will store the list of clauses that loop has visit 
        index = [[i]]
        nextStep = []
        
        while(True):
            # add element from index to mineList 
            mineList.append(index[-1][0])         
             
            # remove all clause that each element in mineList is included    
            for bomb in mineList:
                tmp = []
                for j in tmpPos:
                    if(bomb not in j):
                        tmp.append(j)
                tmpPos = tmp.copy()     # update elements in tmpPos

            # find the next step for mineList 
            if(len(tmpPos)!=0):
                nextStep= tmpPos[0].copy()      # nextStep will be the first element in tmpPos 
                index.append(nextStep)          # add this value into index

            # mineList (the quantity of bomb) is enough 
            if(len(tmpPos) == 0):           
                # check the conflict of mineList 
                if(isConflict(mineList) == False and mineList):
                    return mineList         # not have conflit

                # have conflit
                tmpPos = myPos.copy()   
                mineList.pop(-1)        # remove the last value in mineList        
                index[-1].pop(0)        # remove the corresponding value in index
                while(len(index[-1])==0):       # whether the last index is empty (after removing) ?
                    index.pop(-1)               
                    if(len(index)==0):          # if the "index" is empty, go to the next value in "first" - for loop
                        break
                    index[-1].pop(0)
                    mineList.pop(-1)
                if(len(index) == 0):
                    break
    return None


#Handle for Write to output file
#For Brute Force
def BeforeOutput_1(resList): # resList: list of bombs
    State = [row[:] for row in mine]
    for i in range(len(State)):
        for j in range(len(State[0])):
            idx = i*len(mine) +j+1
            if idx in resList:
                State[i][j] = idx # bomb
            elif not any(idx in clause for clause in cnf.clauses) and not any(-idx in clause for clause in cnf.clauses):
                State[i][j] = 0 # does not have information
            else:
                State[i][j] = -idx # not bomb

    return State

#For Backtracking
def BeforeOutput_2(resList): # resList: list of assigned cells
    State = [row[:] for row in mine]
    for i in range(len(State)):
        for j in range(len(State[0])):
            idx = i*len(mine) +j+1
            if idx in resList:
                State[i][j] = idx # bomb
            elif -idx in resList:
                State[i][j] = -idx # not bomb
            else:
                State[i][j] = 0 # does not have information

    return State

#For A* 
def BeforeOutput_3(resList):  # resList: list of assigned cells
    State = [row[:] for row in mine]
    for i in range(len(State)):
        for j in range(len(State[0])):
            idx = i*len(mine) + j
            State[i][j] = resList[idx]
    return State



#Write to output file
def Display(State, n):
    # define output
    output = [row[:] for row in State]
    adjPoint = [-1, 0 , 1]
    for i in range(len(State)):
        for j in range(len(State[0])):
            if State[i][j] > 0: # check if a bomb
                output[i][j] = 'X'
            elif State[i][j] < 0: # if not -> count number of bombs around
                cnt = 0
                for k in adjPoint:
                    for l in adjPoint:
                        if 0 <= i+k < len(State) and 0 <= j+l < len(State[0]):
                            if State[i + k][j + l] > 0 : # if neighbor is bomb
                                cnt += 1
                output[i][j] = cnt
            elif State[i][j] == 0: # does not have in4
                output[i][j] = '-'
                
    #Write to output file
    f = open("output" + str(n) + '.txt', 'w')    
    for i in range(len(output)):
        for j in range(len(output[0])):
            f.write(str(output[i][j]))
            f.write(' ')
        if i != len(output)-1: 
            f.write('\n')
    f.close()
    
#main program 
if __name__ == '__main__':
    cnf = CNF()
    mine, n = ReadInput()
    print("1. Bruteforce")
    print("2. Backtracking")
    print("3. A*")
    print("4. Use pysat library")
    choice = int(input("Your choice: "))
    # Create CNF
    CreateCNF(mine, cnf)
    
    #Brute Force 
    if choice == 1:
        #calc time
        tracemalloc.start()
        startTime = time.time()
        Output = BruteForce(cnf)
        tracemalloc.stop()
        t = (time.time() - startTime)
        
        #write file
        Display(BeforeOutput_1(Output), n)
        #print time
        print(f"Running time: {t * 1000:.4f} ms")
        
    #Backtracking 
    if choice == 2:
        #calc time
        tracemalloc.start()
        startTime = time.time()
        Output = backtrackingSolver()
        tracemalloc.stop()
        t = (time.time() - startTime)
        
        #write file
        Display(BeforeOutput_2(Output), n)
        #print time
        print(f"Running time: {t * 1000:.4f} ms")
      
    #A*  
    if choice == 3:
        #calc time
        tracemalloc.start()
        startTime = time.time()
        Output = AStar(mine)
        tracemalloc.stop()
        t = (time.time() - startTime)
        
        #write file
        Display(BeforeOutput_3(Output), n)
        #print time
        print(f"Running time: {t * 1000:.4f} ms")

    if choice == 4:
        with Solver(bootstrap_with=cnf) as solver:
            tracemalloc.start()
            startTime = time.time()
            print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')
            print('and the model is:', solver.get_model())
            t = (time.time() - startTime)

            if solver.get_model():
                Display(BeforeOutput_2(solver.get_model()), n)
            #print time
            print(f"Running time: {t * 1000:.4f} ms")