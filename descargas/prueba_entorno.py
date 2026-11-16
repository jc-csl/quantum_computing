"""Práctica 0 (opción D-Wave) — comprobación del entorno."""
import sys, dimod
from dwave.samplers import SimulatedAnnealingSampler
print("Python", sys.version.split()[0], "| dimod", dimod.__version__)
a, b = dimod.Binary("A"), dimod.Binary("B")
H = -3*a - 2*b + 4*(a + b - 1)**2
print("H lineal:", dict(H.linear), "| cuadrático:", dict(H.quadratic), "| offset:", H.offset)
sol = SimulatedAnnealingSampler().sample(H, num_reads=4).first
print("Mejor:", sol.sample, "Energía:", sol.energy)
