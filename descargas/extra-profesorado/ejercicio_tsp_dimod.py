"""
Ejercicio 3 — Viajante (TSP) de 4 ciudades (D-Wave Ocean / dimod)
================================================================
x[c][p] = 1 si la ciudad c ocupa la posición p de la ruta → 16 variables.
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

ciudades = ["A", "B", "C", "D"]
D = [[0, 4, 7, 3],
     [4, 0, 2, 6],
     [7, 2, 0, 5],
     [3, 6, 5, 0]]
n = len(ciudades)
P = 100

x = [[dimod.Binary(f"{ciudades[c]}@{p}") for p in range(n)] for c in range(n)]

# Objetivo: distancia entre la ciudad de la posición p y la de la posición p+1
objetivo = sum(D[i][j] * x[i][p] * x[j][(p + 1) % n]
               for p in range(n) for i in range(n) for j in range(n) if i != j)

# R1: una ciudad por posición · R2: cada ciudad una sola vez
r1 = sum((sum(x[c][p] for c in range(n)) - 1) ** 2 for p in range(n))
r2 = sum((sum(x[c][p] for p in range(n)) - 1) ** 2 for c in range(n))
restriccion = P * (r1 + r2)
H = objetivo + restriccion
print("Variables:", H.num_variables)

res = SimulatedAnnealingSampler().sample(H, num_reads=50, num_sweeps=1000)
cfg = res.first.sample
ruta = []
for p in range(n):
    en_p = [ciudades[c] for c in range(n) if cfg[f"{ciudades[c]}@{p}"]]
    ruta.append(en_p[0] if len(en_p) == 1 else "?")
print("Ruta:", " → ".join(ruta + [ruta[0]]))
print("Distancia:", objetivo.energy(cfg), "| Penalización:", restriccion.energy(cfg))
