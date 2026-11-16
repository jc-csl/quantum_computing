"""
Ejercicio 3 · Repartir tareas entre dos técnicos               (6 variables)
============================================================================
Hay 3 tareas y 2 técnicos. Cada tarea la hace UNA persona.
Queremos el reparto con menos horas en total.

    Horas      Ana   Beñat
    DNS         4      5
    VLAN        6      2
    Backup      3      7

Ejecutar:  python ejercicio3_tareas.py
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS ────────────────────────────────────────────────────────────
personas = ["Ana", "Beñat"]
tareas = ["DNS", "VLAN", "Backup"]
horas = {
    ("Ana", "DNS"): 4,   ("Ana", "VLAN"): 6,   ("Ana", "Backup"): 3,
    ("Beñat", "DNS"): 5, ("Beñat", "VLAN"): 2, ("Beñat", "Backup"): 7,
}
P = 20              # penalización: mayor que cualquier coste de la tabla (7)

# ── 2. VARIABLES BINARIAS: una por cada pareja (persona, tarea) ─────────
# x[("Ana", "DNS")] = 1  →  Ana hace la tarea DNS
x = {}
for p in personas:
    for t in tareas:
        x[(p, t)] = dimod.Binary(f"{p}-{t}")

# ── 3. OBJETIVO: horas totales del reparto ──────────────────────────────
objetivo = sum(horas[k] * x[k] for k in x)

# ── 4. RESTRICCIÓN: cada tarea la hace exactamente una persona ──────────
#   Para DNS:   x(Ana,DNS) + x(Beñat,DNS) = 1   → (… − 1)²
#   y lo mismo para VLAN y Backup. Sumamos las tres penalizaciones.
restriccion = 0
for t in tareas:
    personas_en_t = x[("Ana", t)] + x[("Beñat", t)]
    restriccion = restriccion + P * (personas_en_t - 1) ** 2

# ── 5. HAMILTONIANO ─────────────────────────────────────────────────────
H = objetivo + restriccion

# ── 6. RESOLVER ─────────────────────────────────────────────────────────
resultado = SimulatedAnnealingSampler().sample(H, num_reads=20, seed=42)

# ── 7. INTERPRETAR Y COMPROBAR ──────────────────────────────────────────
cfg = resultado.first.sample
for t in tareas:
    for p in personas:
        if cfg[f"{p}-{t}"] == 1:
            print(f"{t:7s} → {p}")
print("Horas totales:", objetivo.energy(cfg))
print("Penalización:", restriccion.energy(cfg), "(0 = cada tarea tiene una persona)")
