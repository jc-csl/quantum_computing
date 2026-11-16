"""
Ejercicio 2 · Dejar encendidos 2 de 4 servidores               (4 variables)
============================================================================
Por la noche solo hacen falta 2 servidores encendidos.
Queremos elegir EXACTAMENTE 2 con el menor consumo total.

    Servidor   Consumo (W)
    S1         120
    S2          90
    S3         150
    S4          80

Ejecutar:  python ejercicio2_servidores.py
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS ────────────────────────────────────────────────────────────
consumo = {"S1": 120, "S2": 90, "S3": 150, "S4": 80}
K = 2               # cuántos servidores deben quedar encendidos
P = 500             # penalización: mayor que la suma de todos los consumos (440)

# ── 2. VARIABLES BINARIAS: una por servidor ─────────────────────────────
# x["S1"] = 1 → S1 encendido ; 0 → apagado
x = {s: dimod.Binary(s) for s in consumo}

# ── 3. OBJETIVO: consumo total de los encendidos ────────────────────────
# Ya es algo que queremos MINIMIZAR, así que no hace falta signo negativo.
objetivo = sum(consumo[s] * x[s] for s in consumo)

# ── 4. RESTRICCIÓN: exactamente K encendidos ────────────────────────────
#   x_S1 + x_S2 + x_S3 + x_S4 = 2   →   P · (suma − 2)²
encendidos = sum(x.values())
restriccion = P * (encendidos - K) ** 2

# ── 5. HAMILTONIANO ─────────────────────────────────────────────────────
H = objetivo + restriccion

# ── 6. RESOLVER ─────────────────────────────────────────────────────────
resultado = SimulatedAnnealingSampler().sample(H, num_reads=20, seed=42)

# ── 7. INTERPRETAR Y COMPROBAR ──────────────────────────────────────────
cfg = resultado.first.sample
elegidos = [s for s in consumo if cfg[s] == 1]
print("Servidores encendidos:", elegidos)
print("Consumo total:", objetivo.energy(cfg), "W")
print("Penalización:", restriccion.energy(cfg), "(0 = hay exactamente", K, "encendidos)")
