# ── SECCIÓN 6: Código Python completo y comentado ──────────────────────────────
# Ejercicio 1 — Selección del mejor beneficio con QUBO y DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Dadas dos entidades (A y B) con beneficio distinto, elegir EXACTAMENTE UNA
# que maximice el beneficio total. Es el caso más sencillo de optimización
# combinatoria binaria; sirve como base para entender la formulación QUBO.

# ── IMPORTAR DADK ─────────────────────────────────────────────────────────────
# BinPol : clase que representa un Polinomio Binario Cuadrático (QUBO).
#          Internamente almacena un diccionario de términos con sus coeficientes.
#          Admite operaciones aritméticas (+, -, *, **2) entre términos y escalares.
# Term   : representa el monomio  coeficiente × x_índice  (variable binaria).
#          Es la unidad mínima con la que se construye un QUBO.

# QUBOSolverCPU : emula en la CPU local el recocido del Digital Annealer (sin hardware DA).
# Útil para pruebas y problemas pequeños; la API es idéntica al solver real de Fujitsu.
try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS DEL PROBLEMA ────────────────────────────────────────────────────────
beneficio_A = 3   # ganancia si se selecciona la entidad A
beneficio_B = 2   # ganancia si se selecciona la entidad B

# Parámetro de penalización P:
# Debe superar el beneficio máximo obtenible, se aplica si se inc la restricción.
# Si P es demasiado bajo, el solver prefiere incumplir la restricción (más barato).
# Regla práctica: P > max(beneficio_A, beneficio_B) = 3  →  elegimos P = 4.
P = 4

# ── VARIABLES BINARIAS ────────────────────────────────────────────────────────
# Term(coeficiente, índice_de_bit) crea la variable binaria x_índice con ese coef.
# En QUBO todas las variables son binarias: x ∈ {0, 1}.
# Índice 0 → x_A  (x_A = 1 si elegimos entidad A,  0 si no)
# Índice 1 → x_B  (x_B = 1 si elegimos entidad B,  0 si no)
x_A = Term(1, 0)
x_B = Term(1, 1)

# ── OBJETIVO ──────────────────────────────────────────────────────────────────
# Queremos MAXIMIZAR:  f = 3·x_A + 2·x_B
# El solver QUBO siempre MINIMIZA. Cambio de signo para convertir:
#   minimizar(−f)  ⟺  maximizar(f)
# H_obj = −3·x_A − 2·x_B
objetivo = -beneficio_A * x_A - beneficio_B * x_B

# ── RESTRICCIÓN ───────────────────────────────────────────────────────────────
# Exactamente una entidad seleccionada:  x_A + x_B = 1
#
# Técnica estándar en QUBO: penalización cuadrática
#   H_res = P · (x_A + x_B − 1)²
#
# Expansión (recordar que en binario x² = x, pues 0²=0 y 1²=1):
#   = P · (x_A + x_B − 2·x_A·x_B − 1)
#          ↑lineal      ↑cuadrático
#
# Verificación de los cuatro casos posibles:
#   (0,0) → (0+0−1)² = 1  → penaliza  ✗ (nada seleccionado)
#   (1,0) → (1+0−1)² = 0  → no penaliza ✓
#   (0,1) → (0+1−1)² = 0  → no penaliza ✓
#   (1,1) → (1+1−1)² = 1  → penaliza  ✗ (dos seleccionadas)
restriccion = P * (x_A + x_B - 1) ** 2

# ── HAMILTONIANO COMPLETO ─────────────────────────────────────────────────────
# H = H_objetivo + H_restricción
# El solver minimiza H; la solución factible con menor H es el óptimo global.
# Energía esperada: H(x_A=1, x_B=0) = −3 + 0 = −3  (la mejor)
H = objetivo + restriccion

print("Objetivo:    ", objetivo)
print("Restricción: ", restriccion)
print("Hamiltoniano H:", H)
print(f"Número de bits del problema: {H.N}")  # debe ser 2 (un bit por variable)

# ── SOLVER ────────────────────────────────────────────────────────────────────
# number_runs       : búsquedas independientes. Cada run parte de un estado
#                     aleatorio distinto → mayor cobertura del espacio de soluciones.
# number_iterations : pasos de annealing por run. Más pasos → más refinamiento.
# scaling_bit_precision : precisión interna de coeficientes (48 bits es estándar).
#
# ⚠️  NOTA sobre scaling_bit_precision y mejor.energy:
#   El solver escala internamente todos los coeficientes del QUBO a enteros de
#   'scaling_bit_precision' bits. El coeficiente más grande se lleva a ≈ 2^47 y
#   todos los demás se multiplican por el mismo factor (≈ 2^47 / coef_max).
#   Por eso mejor.energy devuelve un número enorme (p.ej. −52 771 280 477 433)
#   en lugar de −3.  Ese valor escalado SOLO sirve para comparar soluciones entre sí.
#   Para obtener la energía real en unidades del problema usa H.compute(config).
number_runs = 4
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=100,         # pocas iteraciones bastan para 2 bits
    scaling_bit_precision=48
)

# minimize(H) ejecuta el annealing y devuelve un objeto SolutionList.
# SolutionList agrupa todas las configuraciones distintas halladas,
# ordenadas de menor a mayor energía.
solution_list = solver.minimize(H)

# min_solution : la solución con la energía más baja (candidato a óptimo global).
mejor = solution_list.min_solution

# ── INTERPRETACIÓN DEL RESULTADO ──────────────────────────────────────────────
# configuration : dict {índice_bit: valor_binario} con la asignación óptima.
# Ejemplo:  {0: 1, 1: 0}  →  x_A=1 (seleccionada), x_B=0 (no seleccionada).
config = mejor.configuration
val_xA = config[0]   # bit 0 → estado de la variable x_A
val_xB = config[1]   # bit 1 → estado de la variable x_B
beneficio_total = beneficio_A * val_xA + beneficio_B * val_xB

print("\n" + "=" * 50)
print("RESULTADO")
print("=" * 50)
print(f"x_A = {val_xA} → Entidad A seleccionada: {'SÍ' if val_xA else 'NO'}")
print(f"x_B = {val_xB} → Entidad B seleccionada: {'SÍ' if val_xB else 'NO'}")
print(f"Beneficio total: {beneficio_total}")

# H.compute(config) evalúa el polinomio H en la configuración encontrada.
# Devuelve la energía REAL en unidades del problema (no la escalada internamente).
# Si la restricción se cumple (penalización = 0):  energy = −beneficio_total.
print(f"Energía mínima H: {H.compute(config)}")

# compute(config) evalúa el polinomio restriccion numéricamente.
# Debe ser 0.0 si la restricción se cumple; cualquier valor > 0 indica incumplimiento.
print(f"Penalización de restricción: {restriccion.compute(config)}")

# frequency : en cuántos de los number_runs se llegó a esta misma solución.
# Alta frecuencia indica convergencia robusta del solver al óptimo.
print(f"Frecuencia: {int(mejor.frequency)} de {number_runs} runs")
print(f"Restricción x_A+x_B=1: {'cumplida ✓' if val_xA + val_xB == 1 else 'INCUMPLIDA ✗'}")

# ── TABLA DE SOLUCIONES ENCONTRADAS ───────────────────────────────────────────
# solution_list.solutions lista TODAS las configuraciones distintas halladas,
# ordenadas de mejor (menor H) a peor. Permite analizar el "paisaje energético":
# cuántas soluciones factibles e infactibles encontró el solver y con qué frecuencia.
print("\nSoluciones encontradas por el solver:")
print(f"{'xA':>3} {'xB':>3} {'Beneficio':>10} {'H':>8} {'Frecuencia':>11}")
print("-" * 42)
for sol in solution_list.solutions:
    xa = sol.configuration[0]
    xb = sol.configuration[1]
    ben = beneficio_A * xa + beneficio_B * xb
    # H.compute() devuelve la energía real; sol.energy es la versión escalada internamente.
    print(f"{xa:>3} {xb:>3} {ben:>10} {H.compute(sol.configuration):>8.1f} {int(sol.frequency):>11}")