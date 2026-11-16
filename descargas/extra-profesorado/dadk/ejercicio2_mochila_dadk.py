# ── SECCIÓN 6: Código Python completo y comentado ──────────────────────────────
# Ejercicio 2 — Mochila pequeña con DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Seleccionar un subconjunto de elementos (equipos de red) maximizando el valor
# total sin superar la capacidad de la mochila (peso máximo permitido).
# Es el problema de la mochila 0/1 (Knapsack), NP-difícil en su forma general.
#
try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS ─────────────────────────────────────────────────────────────────────
# Cada elemento tiene un valor (beneficio) y un peso (recurso consumido).
elementos = ["Router", "Switch", "Punto de acceso", "Cableado"]
valores   = [8, 6, 5, 4]   # valor/utilidad de cada elemento
pesos     = [3, 2, 2, 1]   # peso/recurso que consume cada elemento
capacidad = 5              # límite máximo de peso total admitido

# P debe ser mayor que el valor máximo alcanzable (suma de todos los valores = 23).
# Si P es pequeño el solver puede obtener más beneficio ignorando la restricción.
P = 30  # 30 > 23 (suma total de valores) → penalización dominante

# Número de elementos del problema
n = len(elementos)

# ── VARIABLES DE ELEMENTOS ────────────────────────────────────────────────────
# x[i] = 1 → el elemento i SE INCLUYE en la mochila
# x[i] = 0 → el elemento i NO SE INCLUYE
# Bits 0..n-1 representan las decisiones sobre los elementos.
# x[0] → Router  |  x[1] → Switch  |  x[2] → Punto de acceso  |  x[3] → Cableado
x = [Term(1, i) for i in range(n)]

# ── VARIABLES DE HOLGURA (SLACK) ──────────────────────────────────────────────
# Problema: la restricción  Σ pesos·x_i ≤ capacidad  es una DESIGUALDAD.
# QUBO solo puede representar igualdades de forma directa.
# Solución: introducir una variable entera de holgura  s  tal que:
#   Σ pesos·x_i + s = capacidad   (convierte ≤ en =)
# La holgura representa el espacio libre restante en la mochila.
#
# Codificación binaria de s ∈ [0, capacidad]:
#   s = y0·1 + y1·2 + y2·4   (representación binaria con 3 bits)
#   Rango posible: 0..7  (cubre 0..capacidad=5 con margen).
#
# ¿Por qué 3 bits?  ceil(log2(capacidad + 1)) = ceil(log2(6)) = 3.
# Los índices de estos bits siguen a los de los elementos (4, 5, 6).
y0 = Term(1, 4)   # bit 4: peso 1 (2⁰)
y1 = Term(1, 5)   # bit 5: peso 2 (2¹)
y2 = Term(1, 6)   # bit 6: peso 4 (2²)
slack = y0 + 2*y1 + 4*y2   # valor entero que representa la holgura

# ── OBJETIVO ──────────────────────────────────────────────────────────────────
# Maximizar Σ valores[i]·x[i]  →  minimizar el negativo (conversión QUBO estándar).
# BinPol.sum() es equivalente a Python sum() pero opera sobre objetos BinPol/Term.
objetivo = BinPol.sum(-valores[i] * x[i] for i in range(n))

# ── RESTRICCIÓN DE CAPACIDAD ──────────────────────────────────────────────────
# Penalización cuadrática de la igualdad:  peso_total + slack = capacidad
#   H_res = P · (Σ pesos[i]·x[i] + slack − capacidad)²
#
# Cuando se cumple la igualdad el cuadrado vale 0  →  sin penalización.
# Cuando se incumple (se excede la capacidad o la holgura no cuadra) el término
# cuadrático introduce una energía positiva que el solver evita.
peso_total  = BinPol.sum(pesos[i] * x[i] for i in range(n))
restriccion = P * (peso_total + slack - capacidad) ** 2

# ── HAMILTONIANO ──────────────────────────────────────────────────────────────
# H total = objetivo + restricción
# El espacio de búsqueda tiene 2^7 = 128 configuraciones posibles (4 elementos + 3 bits slack).
H = objetivo + restriccion

print(f"Hamiltoniano creado con {H.N} bits")
print("Bits 0-3: elementos | Bits 4-6: holgura (slack)")

# ── SOLVER ────────────────────────────────────────────────────────────────────
# Aumentamos number_runs e iterations respecto al Ejercicio 1 porque el espacio
# de búsqueda es mayor (7 bits = 128 combinaciones vs. 2 bits = 4 combinaciones).
number_runs = 12
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=800,    # más iteraciones para explorar mejor el espacio
    scaling_bit_precision=48
)
solution_list = solver.minimize(H)
mejor         = solution_list.min_solution
config        = mejor.configuration   # dict {bit_index: 0_o_1}

# ── INTERPRETACIÓN DEL RESULTADO ──────────────────────────────────────────────
# Reconstruimos qué elementos se seleccionaron leyendo los bits 0..n-1.
seleccionados  = [elementos[i] for i in range(n) if config[i] == 1]
valor_obtenido = sum(valores[i] for i in range(n) if config[i] == 1)
peso_obtenido  = sum(pesos[i]   for i in range(n) if config[i] == 1)

# Reconstruimos el valor de la holgura a partir de los bits 4-6.
# config[4]·1 + config[5]·2 + config[6]·4 debe igualar (capacidad - peso_obtenido).
slack_obtenido = config[4] + 2*config[5] + 4*config[6]

print("\nRESULTADO MOCHILA")
print("=" * 60)
print(f"Elementos seleccionados : {seleccionados}")
print(f"Valor obtenido          : {valor_obtenido}")
print(f"Peso utilizado          : {peso_obtenido} / {capacidad}")
print(f"Holgura codificada      : {slack_obtenido}  (espacio libre en la mochila)")
# Verificación: peso + holgura debe ser exactamente igual a la capacidad.
print(f"Restricción (peso+slack = capacidad): {peso_obtenido}+{slack_obtenido} = {peso_obtenido+slack_obtenido}  ({'✓' if peso_obtenido+slack_obtenido==capacidad else '✗'})")
# H.compute(config) devuelve la energía real del problema (no la escalada internamente).
print(f"Energía H               : {H.compute(config)}")
# Penalización 0.0 confirma que la restricción de capacidad se respeta exactamente.
print(f"Penalización            : {restriccion.compute(config)}")
print(f"Frecuencia              : {int(mejor.frequency)} de {number_runs} runs")

# ── TABLA RESUMEN ─────────────────────────────────────────────────────────────
# Muestra las 8 mejores soluciones halladas para comparar factibles vs. infactibles.
# Las soluciones con Penaliz. = 0 son las únicas que respetan la capacidad.
print("\nSoluciones encontradas (top 8):")
print(f"{'Bits':>7} {'Valor':>7} {'Peso':>6} {'Slack':>7} {'Penaliz.':>9} {'H':>8} {'Freq':>6}")
print("-" * 56)
for sol in solution_list.solutions[:8]:
    cfg  = sol.configuration
    # Bits 0-3: elementos incluidos (1) o excluidos (0)
    bits = ''.join(str(cfg[i]) for i in range(n))
    val  = sum(valores[i] for i in range(n) if cfg[i] == 1)
    pes  = sum(pesos[i]   for i in range(n) if cfg[i] == 1)
    sl   = cfg[4] + 2*cfg[5] + 4*cfg[6]   # valor de holgura decodificado
    pen  = restriccion.compute(cfg)         # 0.0 → factible, >0 → infactible
    # H.compute() devuelve la energía real; sol.energy es la versión escalada internamente.
    print(f"{bits:>7} {val:>7} {pes:>6} {sl:>7} {pen:>9.1f} {H.compute(sol.configuration):>8.1f} {int(sol.frequency):>6}")