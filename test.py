from pysat.formula import CNF
from pysat.solvers import Solver
import numpy as np
# a = [4, 5]
# b = [-4, 5, -6]
# a.extend(b)
# print(a)
# print(list(set(a)))

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


cnf = CNF(from_clauses=[[4, 5], [4, 5, 6], [-4, -5], [-4, -6], [-5, -6], [5, 6], [4, 5, 6, 7], [4, 5, 6, 9], [4, 5, 7, 9], [4, 6, 7, 9], [5, 6, 7, 9], [-4, -5, -6], [-4, -5, -7], [-4, -5, -9], [-4, -6, -7], [-4, -6, -9], [-4, -7, -9], [-5, -6, -7], [-5, -6, -9], [-5, -7, -9], [-6, -7, -9]])
print(resolution(cnf))