# ── SECCIÓN 6: Código Python completo y comentado ──────────────────────────────
# Ejercicio 6 — Number Partitioning con DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Dividir un conjunto de números en dos grupos (A y B) tal que la diferencia
# entre la suma de ambos grupos sea mínima (idealmente = 0).
# Number Partitioning es NP-completo en su forma de decisión.
#


try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS ─────────────────────────────────────────────────────────────────────
numeros    = [3, 5, 6, 10]   # valores a repartir entre los dos grupos
n          = len(numeros)    # 4 números → 4 bits
suma_total = sum(numeros)    # suma_total = 24; para equilibrio perfecto cada grupo = 12

# ── VARIABLES BINARIAS ────────────────────────────────────────────────────────
# x[i] = 1 → el número numeros[i] va al GRUPO A
# x[i] = 0 → el número numeros[i] va al GRUPO B
# Con 4 números hay 2^4 = 16 posibles repartos.
x = [Term(1, i) for i in range(n)]

# ── HAMILTONIANO ──────────────────────────────────────────────────────────────
# Derivación matemática:
#   suma_A = Σ numeros[i] · x[i]          (suma del grupo A)
#   suma_B = suma_total − suma_A           (suma del grupo B, no necesita bits extra)
#   diferencia = suma_A − suma_B
#              = suma_A − (suma_total − suma_A)
#              = 2·suma_A − suma_total
#
# Objetivo: minimizar |diferencia| = |2·suma_A − suma_total|
# En QUBO minimizamos el cuadrado (equivalente, ya que (dif=0) ⟺ (dif²=0)):
#   H = (2·suma_A − suma_total)²
#
# Mínimo global: H = 0  ⟺  suma_A = suma_total / 2 = 12
# No requiere penalización: H ya es 0 en la solución óptima y positivo en el resto.
suma_A = BinPol.sum(numeros[i] * x[i] for i in range(n))
H = (2 * suma_A - suma_total) ** 2

print(f"Hamiltoniano Number Partitioning creado con {H.N} bits")
print(f"Suma total: {suma_total}  |  Objetivo: suma A = {suma_total//2}")

# ── SOLVER ────────────────────────────────────────────────────────────────────
# No hay restricciones adicionales: toda configuración binaria es factible.
# El solver simplemente busca el mínimo de H = (2·suma_A − suma_total)².
number_runs = 8
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=500,
    scaling_bit_precision=48
)
solution_list = solver.minimize(H)
mejor  = solution_list.min_solution
config = mejor.configuration   # dict {bit: 0_o_1}

# ── INTERPRETACIÓN DEL RESULTADO ──────────────────────────────────────────────
# Separamos los números en grupo A (bit=1) y grupo B (bit=0).
grupo_A     = [numeros[i] for i in range(n) if config[i] == 1]
grupo_B     = [numeros[i] for i in range(n) if config[i] == 0]
suma_A_real = sum(grupo_A)
suma_B_real = sum(grupo_B)
diferencia  = abs(suma_A_real - suma_B_real)

print("\nRESULTADO NUMBER PARTITIONING")
print("=" * 60)
print(f"Grupo A: {grupo_A}  →  suma {suma_A_real}")
print(f"Grupo B: {grupo_B}  →  suma {suma_B_real}")
print(f"Diferencia absoluta: {diferencia}")
# H.compute(config) devuelve la energía real (= diferencia²).
# Si diferencia=0 → H=0 (equilibrio perfecto).
print(f"Energía H (= diferencia²): {H.compute(config)}")
print(f"Frecuencia: {int(mejor.frequency)} de {number_runs} runs")
if diferencia == 0:
    print("✓ Partición perfectamente equilibrada")
else:
    # Para este conjunto de números puede no existir partición con diferencia 0
    # (depende de si suma_total es par y de si hay subconjunto que sume exactamente la mitad).
    print(f"  La mejor partición posible tiene diferencia {diferencia}")

# ── TABLA DE SOLUCIONES ───────────────────────────────────────────────────────
# La tabla permite ver todas las particiones y su desequilibrio.
# Las filas con dif=0 son particiones perfectas; con dif pequeña, cuasi-óptimas.
print("\nSoluciones encontradas:")
print(f"{'bits':>6} {'grupo A':>18} {'suma A':>8} {'suma B':>8} {'dif':>5} {'H':>8} {'freq':>6}")
print("-" * 62)
for sol in solution_list.solutions[:8]:
    cfg  = sol.configuration
    gA   = [numeros[i] for i in range(n) if cfg[i] == 1]
    sA   = sum(gA)
    sB   = suma_total - sA                 # suma B = total − suma A (no necesita leer bits)
    bits = ''.join(str(cfg[i]) for i in range(n))  # representación binaria de la partición
    # dif = |sA − sB| = |2·sA − suma_total|; coincide con sqrt(H) si H = dif².
    # H.compute() devuelve la energía real; sol.energy es la versión escalada internamente.
    print(f"{bits:>6} {str(gA):>18} {sA:>8} {sB:>8} {abs(sA-sB):>5} {H.compute(sol.configuration):>8.1f} {int(sol.frequency):>6}")