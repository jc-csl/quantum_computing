"""
Ejercicio 4 · Equilibrar máquinas virtuales entre dos hosts    (4 variables)
============================================================================
Tenemos 4 máquinas virtuales con esta RAM: 3, 5, 6 y 10 GB (total 24 GB).
Queremos repartirlas en dos hosts (A y B) con la RAM lo más igualada posible.
Lo ideal sería 12 GB en cada uno.

Este problema NO tiene restricciones: solo función objetivo.

Ejecutar:  python ejercicio4_particion.py
"""
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS ────────────────────────────────────────────────────────────
ram = {"VM1": 3, "VM2": 5, "VM3": 6, "VM4": 10}
total = sum(ram.values())                      # 24

# ── 2. VARIABLES BINARIAS: una por máquina ──────────────────────────────
# x["VM1"] = 1 → VM1 va al host A ;  0 → va al host B
x = {vm: dimod.Binary(vm) for vm in ram}

# ── 3. OBJETIVO ─────────────────────────────────────────────────────────
# RAM del host A = suma de las VMs con x = 1
ram_A = sum(ram[vm] * x[vm] for vm in ram)
# Diferencia entre hosts = ram_A − ram_B = ram_A − (total − ram_A) = 2·ram_A − total
# La elevamos al cuadrado: siempre ≥ 0 y vale 0 si el reparto es perfecto.
H = (2 * ram_A - total) ** 2

# ── 4. (sin restricciones) ──────────────────────────────────────────────
# ── 5. H ya está construido ─────────────────────────────────────────────

# ── 6. RESOLVER ─────────────────────────────────────────────────────────
resultado = SimulatedAnnealingSampler().sample(H, num_reads=20, seed=42)

# ── 7. INTERPRETAR ──────────────────────────────────────────────────────
cfg = resultado.first.sample
host_A = [vm for vm in ram if cfg[vm] == 1]
host_B = [vm for vm in ram if cfg[vm] == 0]
gb_A = sum(ram[vm] for vm in host_A)
print("Host A:", host_A, "→", gb_A, "GB")
print("Host B:", host_B, "→", total - gb_A, "GB")
print("Diferencia:", abs(2 * gb_A - total), "GB  | Energía:", resultado.first.energy)
