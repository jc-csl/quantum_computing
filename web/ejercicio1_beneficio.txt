"""
Ejercicio 1 · Elegir el proyecto con más beneficio            (2 variables)
============================================================================
Tenemos dos proyectos y solo podemos hacer UNO:
    Proyecto A → beneficio 3
    Proyecto B → beneficio 2
¿Cuál elegimos? (La respuesta es obvia: A. Sirve para aprender el método.)

Ejecutar:  python ejercicio1_beneficio.py
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS ────────────────────────────────────────────────────────────
beneficio_A = 3
beneficio_B = 2
P = 4               # peso de la penalización: mayor que el beneficio máximo (3)

# ── 2. VARIABLES BINARIAS: una por cada decisión SÍ/NO ─────────────────
x_A = dimod.Binary("A")      # vale 1 si elijo el proyecto A, 0 si no
x_B = dimod.Binary("B")      # vale 1 si elijo el proyecto B, 0 si no

# ── 3. OBJETIVO ─────────────────────────────────────────────────────────
# Queremos MAXIMIZAR el beneficio, pero el solver siempre MINIMIZA.
# Truco: lo escribimos en negativo → más beneficio = energía más baja.
objetivo = -beneficio_A * x_A - beneficio_B * x_B

# ── 4. RESTRICCIÓN → PENALIZACIÓN ───────────────────────────────────────
# "Exactamente uno":  x_A + x_B = 1
# Al elevar al cuadrado vale 0 si se cumple y algo positivo si no.
restriccion = P * (x_A + x_B - 1) ** 2

# ── 5. HAMILTONIANO H = objetivo + penalización (esto es el QUBO) ───────
H = objetivo + restriccion
print("Modelo QUBO generado por dimod:")
print("  lineal    :", dict(H.linear))       # {'A': -7.0, 'B': -6.0}
print("  cuadrático:", dict(H.quadratic))    # {('B', 'A'): 8.0}
print("  constante :", H.offset)             # 4.0

# ── 6. RESOLVER ─────────────────────────────────────────────────────────
# Con solo 2 variables podemos ver TODAS las combinaciones (fuerza bruta):
print("\nTodas las combinaciones, de mejor a peor:")
print(dimod.ExactSolver().sample(H))

# Y con el recocido simulado (lo que usaríamos en problemas grandes):
sampler = SimulatedAnnealingSampler()
resultado = sampler.sample(H, num_reads=10, seed=42)   # 10 intentos

# ── 7. INTERPRETAR Y COMPROBAR ──────────────────────────────────────────
mejor = resultado.first        # la muestra con menor energía
cfg = mejor.sample             # diccionario, p. ej. {'A': 1, 'B': 0}

print("\nMejor solución:", cfg)
if cfg["A"] == 1:
    print("→ Se elige el proyecto A")
if cfg["B"] == 1:
    print("→ Se elige el proyecto B")
print("Energía:", mejor.energy, "(= −beneficio)")
print("Penalización:", restriccion.energy(cfg), "(0 = cumple la restricción)")
