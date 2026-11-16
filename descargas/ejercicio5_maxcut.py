"""
Ejercicio 5 · Max-Cut: dividir una red en dos grupos           (7 variables)
============================================================================
Una red de 7 equipos. Queremos separarlos en dos grupos (A y B) de forma
que el MÁXIMO número de conexiones (aristas) quede entre grupos distintos.
Este problema NO tiene restricciones: solo función objetivo.

Ejecutar:  python ejercicio5_maxcut.py
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS: las conexiones de la red ──────────────────────────────────
aristas = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 3),
           (2, 5), (3, 6), (4, 5), (4, 6), (5, 6)]
n = 7

# ── 2. VARIABLES BINARIAS: una por nodo ─────────────────────────────────
# x[i] = 0 → nodo i en el grupo A ;  x[i] = 1 → nodo i en el grupo B
x = [dimod.Binary(i) for i in range(n)]

# ── 3. OBJETIVO ─────────────────────────────────────────────────────────
# Una arista (i, j) está "cortada" si sus nodos están en grupos distintos.
#   x_i + x_j − 2·x_i·x_j  vale 1 si x_i ≠ x_j  y 0 si son iguales.
# Queremos MAXIMIZAR las cortadas → minimizamos su negativo.
H = 0
for i, j in aristas:
    cortada = x[i] + x[j] - 2 * x[i] * x[j]
    H = H - cortada

# ── 4-5. (sin restricciones: H ya está construido) ─────────────────────

# ── 6. RESOLVER ─────────────────────────────────────────────────────────
resultado = SimulatedAnnealingSampler().sample(H, num_reads=20, seed=42)

# ── 7. INTERPRETAR ──────────────────────────────────────────────────────
cfg = resultado.first.sample
grupo_A = [i for i in range(n) if cfg[i] == 0]
grupo_B = [i for i in range(n) if cfg[i] == 1]
cortadas = [(i, j) for i, j in aristas if cfg[i] != cfg[j]]
print("Grupo A:", grupo_A)
print("Grupo B:", grupo_B)
print("Aristas cortadas:", len(cortadas), "de", len(aristas))
print("Energía:", resultado.first.energy, "(= −aristas cortadas)")
