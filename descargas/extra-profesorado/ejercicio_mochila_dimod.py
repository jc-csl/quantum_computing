"""
Ejercicio 2 — Mochila (D-Wave Ocean / dimod)
============================================
Material para un armario de red con capacidad 5.
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

nombres  = ["Router", "Switch", "Punto de acceso", "Cableado"]
valores  = [8, 6, 5, 4]
pesos    = [3, 2, 2, 1]
capacidad = 5
P = 30

# Variables de los elementos y bits de holgura (s = y0 + 2·y1 + 4·y2 → 0..7)
x = [dimod.Binary(n) for n in nombres]
y = [dimod.Binary(f"s{k}") for k in range(3)]
holgura = sum(2**k * y[k] for k in range(3))

objetivo    = -sum(v * xi for v, xi in zip(valores, x))
peso_total  = sum(w * xi for w, xi in zip(pesos, x))
restriccion = P * (peso_total + holgura - capacidad) ** 2   # ≤ C  →  = C con holgura
H = objetivo + restriccion
print("Variables:", H.num_variables, "| términos cuadráticos:", len(H.quadratic))

res = SimulatedAnnealingSampler().sample(H, num_reads=20, num_sweeps=500)
mejor = res.first
cfg = mejor.sample
elegidos = [n for n in nombres if cfg[n] == 1]
print("Elegidos:", elegidos)
print("Valor:", sum(v for v, n in zip(valores, nombres) if cfg[n]),
      "| Peso:", sum(w for w, n in zip(pesos, nombres) if cfg[n]), "/", capacidad)
print("Energía:", mejor.energy, "| Penalización:", restriccion.energy(cfg))

print("\nTop 5 soluciones distintas:")
for s, e, n in res.aggregate().data(["sample", "energy", "num_occurrences"]):
    print(f"  E={e:6.0f}  x{n:2d}  ", [k for k in nombres if s[k]])
