"""Práctica 0 — comprobación del entorno."""
import sys
print("Python", sys.version.split()[0])
try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

x0, x1 = Term(1, 0), Term(1, 1)
H = -3*x0 - 2*x1 + 4*(x0 + x1 - 1)**2
print("H =", H)
sol = QUBOSolverCPU(number_runs=4, number_iterations=100).minimize(H).min_solution
print("Mejor:", sol.configuration, "Energía:", H.compute(sol.configuration))
