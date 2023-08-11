from pysat.solvers import Glucose3
from pysat.formula import CNF

# Định nghĩa tập mệnh đề CNF
clauses = [
    [-2]
[-6]
[3, 5, 10]
[-3, -5]
[-3, -10]
[-5, -10]
[2, 3, 6]
[2, 3, 12]
[2, 6, 12]
[3, 6, 12]
[-2, -3]
[-2, -6]
[-2, -12]
[-3, -6]
[-3, -12]
[-6, -12]
[2, 3, 12, 14]
[-2, -3, -12]
[-2, -3, -14]
[-2, -12, -14]
[-3, -12, -14]
[-3]
[-5]
[-10]
[-14]
[6]
[12]
[17]
[-12]
[-17]
[-18]
[10, 14]
[10, 20]
[14, 20]
[-21]
[14, 18, 20]
[-14, -18]
[-14, -20]
[-18, -20]
[17, 18, 21]
[-17, -18]
[-17, -21]
[-18, -21]
[17, 18]
[18, 20]
[20]
    # ... các mệnh đề khác ...
]

# Tạo một solver Glucose3
with Glucose3() as solver:
    # Thêm các mệnh đề vào solver
    solver.append_formula(clauses)

    # Giải quyết bài toán SAT
    if solver.solve():
        model = solver.get_model()
        print("Solution:", model)
    else:
        print("Unsatisfiable")
