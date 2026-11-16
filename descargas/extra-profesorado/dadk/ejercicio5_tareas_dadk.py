# ── Código Python completo y comentado ──────────────────────────────
# Ejercicio 5 — Reparto de tareas con DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Asignar n_tareas tareas a n_personas personas minimizando el coste total,
# con la restricción de que cada tarea sea asignada a exactamente una persona.
# Es el Problema de Asignación Lineal (LAP), resoluble en tiempo polinomial
# con el algoritmo húngaro, pero aquí lo formulamos como QUBO para practicar.
#


try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS ─────────────────────────────────────────────────────────────────────
personas = ["Ana", "Beñat"]
tareas   = ["DNS", "VLAN", "Backup"]

# Matriz de costes: costes[p][t] = coste de que la persona p realice la tarea t.
# Coste puede representar tiempo, dificultad estimada o coste económico.
costes = [
    [4, 6, 3],   # Ana:   DNS=4, VLAN=6, Backup=3  → Ana es mejor en DNS y Backup
    [5, 2, 7],   # Beñat: DNS=5, VLAN=2, Backup=7  → Beñat es mejor en VLAN
]

# P debe superar la diferencia máxima de coste entre personas para cualquier tarea.
# Diferencia máxima: |7 − 3| = 4 (tarea Backup). P=20 >> 4 → restricción dominante.
P = 20

num_personas = len(personas)   # 2
num_tareas   = len(tareas)     # 3

# ── FUNCIONES DE ÍNDICE ───────────────────────────────────────────────────────
# Necesitamos num_personas × num_tareas = 2×3 = 6 variables binarias.
# Mapeamos la pareja (persona p, tarea t) a un índice lineal de bit:
#   (Ana, DNS)=0  (Ana, VLAN)=1  (Ana, Backup)=2
#   (Beñat,DNS)=3 (Beñat,VLAN)=4 (Beñat,Backup)=5
def idx(p, t):
    """Convierte la pareja (persona p, tarea t) en un índice lineal de bit."""
    return p * num_tareas + t

# x(p, t) = 1 si la persona p realiza la tarea t, 0 si no.
def x(p, t):
    return Term(1, idx(p, t))

# ── OBJETIVO ──────────────────────────────────────────────────────────────────
# Minimizar el coste total de todas las asignaciones activas (x=1).
# Aquí no hay cambio de signo: ya es una minimización directa de costes.
# H_obj = Σ_{p,t} costes[p][t] · x(p,t)
objetivo = BinPol.sum(
    costes[p][t] * x(p, t)
    for p in range(num_personas)
    for t in range(num_tareas)
)

# ── RESTRICCIÓN: CADA TAREA ASIGNADA A EXACTAMENTE UNA PERSONA ────────────────
# Para cada tarea t:  Σ_p x(p,t) = 1
# Penalización cuadrática:  P · (Σ_p x(p,t) − 1)²
#
# Verificación para la tarea DNS (t=0):
#   Ana=0, Beñat=0 → (0+0−1)²=1 → penaliza (tarea sin asignar) ✗
#   Ana=1, Beñat=0 → (1+0−1)²=0 → no penaliza ✓
#   Ana=0, Beñat=1 → (0+1−1)²=0 → no penaliza ✓
#   Ana=1, Beñat=1 → (1+1−1)²=1 → penaliza (dos personas para la misma tarea) ✗
restriccion = P * BinPol.sum(
    (BinPol.sum(x(p, t) for p in range(num_personas)) - 1) ** 2
    for t in range(num_tareas)   # una restricción independiente por cada tarea
)

# ── HAMILTONIANO ──────────────────────────────────────────────────────────────
H = objetivo + restriccion
print(f"Hamiltoniano de asignación creado con {H.N} bits")
print(f"({num_personas} personas × {num_tareas} tareas = {num_personas*num_tareas} bits)")

# ── SOLVER ────────────────────────────────────────────────────────────────────
# Espacio de búsqueda: 2^6 = 64 configuraciones posibles.
# Soluciones factibles: aquellas donde cada tarea tiene exactamente una persona.
# Número de soluciones factibles: num_personas^num_tareas = 2^3 = 8.
number_runs = 8
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=700,
    scaling_bit_precision=48
)
solution_list = solver.minimize(H)
mejor  = solution_list.min_solution
config = mejor.configuration   # dict con 6 bits indexados por idx(p,t)

# ── INTERPRETACIÓN DEL RESULTADO ──────────────────────────────────────────────
# Para cada tarea buscamos qué persona tiene el bit activo (x(p,t)=1).
asignaciones = []
coste_total  = 0
for t in range(num_tareas):
    asignada = None
    for p in range(num_personas):
        if config[idx(p, t)] == 1:
            asignada = p               # persona p tiene asignada la tarea t
            coste_total += costes[p][t]
    asignaciones.append((tareas[t], personas[asignada] if asignada is not None else "SIN ASIGNAR"))

print("\nRESULTADO REPARTO DE TAREAS")
print("=" * 60)
for tarea, persona in asignaciones:
    t_idx    = tareas.index(tarea)
    p_idx    = personas.index(persona) if persona in personas else -1
    coste_t  = costes[p_idx][t_idx] if p_idx >= 0 else "?"
    print(f"  {tarea:>8} → {persona:<8}  (coste: {coste_t})")
print(f"Coste total    : {coste_total}")   # solución óptima esperada: 4+2+3 = 9

# Penalización = 0 confirma que cada tarea fue asignada a exactamente una persona.
print(f"Penalización   : {restriccion.compute(config)}")
# H.compute(config) devuelve la energía real; debe igualar el coste total si la restricción se cumple.
print(f"Energía H      : {H.compute(config)}")
print(f"Frecuencia     : {int(mejor.frequency)} de {number_runs} runs")

# ── MATRIZ PERSONA-TAREA ──────────────────────────────────────────────────────
# La matriz de asignación debe tener exactamente un 1 por columna (una persona por tarea).
# Si alguna columna tiene 0 o 2 unos, la restricción fue incumplida.
print("\nMatriz x_{persona, tarea}:")
print("          " + "  ".join(f"{t:>8}" for t in tareas))
for p in range(num_personas):
    fila = [str(config[idx(p, t)]) for t in range(num_tareas)]
    # Un 1 en la posición (p,t) indica que la persona p realiza la tarea t.
    print(f"{personas[p]:>8}: " + "  ".join(f"{v:>8}" for v in fila))