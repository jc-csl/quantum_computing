# ── SECCIÓN 6: Código Python completo y comentado ──────────────────────────────
# Ejercicio 3 — TSP de 4 ciudades con DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Encontrar el ciclo hamiltoniano de menor coste que visita 4 ciudades exactamente
# una vez y regresa al origen (Travelling Salesman Problem, TSP).
# El TSP es NP-completo; para 4 ciudades hay (4-1)!/2 = 3 rutas distintas.
#
# Analogía en incumplir: optimizar la ruta de visitas a distintos centros de datos
# (o nodos de red) minimizando la latencia/coste total del recorrido.

try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS ─────────────────────────────────────────────────────────────────────
ciudades = ["A", "B", "C", "D"]   # 4 nodos del grafo completo

# Matriz de distancias (simétrica): distancias[i][j] = coste de viajar de i a j.
# En redes: podría representar latencia, coste de enlace o distancia física.
distancias = [
    [0, 4, 7, 3],   # desde A: a B=4, a C=7, a D=3
    [4, 0, 2, 6],   # desde B: a A=4, a C=2, a D=6
    [7, 2, 0, 5],   # desde C: a A=7, a B=2, a D=5
    [3, 6, 5, 0],   # desde D: a A=3, a B=6, a C=5
]
n = len(ciudades)   # n = 4

# P debe ser mucho mayor que la distancia máxima del ciclo (peor caso ≈ 4·7 = 28).
# Elegimos P = 100 >> 28 para garantizar que las restricciones dominen al objetivo.
P = 100

# ── FUNCIONES DE ÍNDICE ───────────────────────────────────────────────────────
# El TSP usa n×n variables binarias x_{ciudad, posición}.
# Para operar con vectores planos de bits necesitamos una función de mapeo:
#   idx(c, p)  →  índice lineal del bit correspondiente a (ciudad c, posición p)
#
# Esquema de indexación (n=4):
#   posición →   0    1    2    3
#   ciudad A:  bit0  bit1  bit2  bit3
#   ciudad B:  bit4  bit5  bit6  bit7
#   ciudad C:  bit8  bit9  bit10 bit11
#   ciudad D: bit12 bit13 bit14 bit15
# Total: n×n = 4×4 = 16 bits.
def idx(c, p):
    """Convierte la pareja (ciudad c, posición p) en un índice lineal de bit."""
    return c * n + p

# x(c, p) devuelve el Term (variable binaria) x_{c,p}.
# x_{c,p} = 1 significa "la ciudad c ocupa la posición p en la ruta".
def x(c, p):
    return Term(1, idx(c, p))

# ── OBJETIVO: DISTANCIA TOTAL DEL CICLO ───────────────────────────────────────
# Para cada posición p del ciclo, si la ciudad i está en p y la j en p+1,
# se acumula el coste distancias[i][j].
# El operador % cierra el ciclo: la posición siguiente a la última (n-1) es la 0.
#
# Término cuadrático:  distancias[i][j] · x(i,p) · x(j,(p+1)%n)
# Solo contribuye cuando x(i,p)=1 AND x(j,p+1)=1 simultáneamente.
objetivo = BinPol.sum(
    distancias[i][j] * x(i, p) * x(j, (p + 1) % n)
    for p in range(n)      # para cada posición del ciclo
    for i in range(n)      # ciudad en la posición actual
    for j in range(n)      # ciudad en la posición siguiente
    if i != j              # excluir auto-loops (una ciudad no va a sí misma)
)

# ── RESTRICCIÓN 1: EXACTAMENTE UNA CIUDAD POR POSICIÓN ───────────────────────
# Cada posición del ciclo debe estar ocupada por exactamente una ciudad.
# Para la posición p:  Σ_c x_{c,p} = 1
# Penalización:  P · (Σ_c x_{c,p} − 1)²
# Si hay 0 o 2+ ciudades en la misma posición el término cuadrático es positivo.
r1 = BinPol.sum(
    (BinPol.sum(x(c, p) for c in range(n)) - 1) ** 2
    for p in range(n)   # una restricción por cada posición del ciclo
)

# ── RESTRICCIÓN 2: CADA CIUDAD APARECE EXACTAMENTE UNA VEZ ───────────────────
# Cada ciudad debe aparecer en exactamente una posición del ciclo.
# Para la ciudad c:  Σ_p x_{c,p} = 1
# Penalización:  P · (Σ_p x_{c,p} − 1)²
# Si una ciudad no aparece o aparece repetida, el término cuadrático es positivo.
r2 = BinPol.sum(
    (BinPol.sum(x(c, p) for p in range(n)) - 1) ** 2
    for c in range(n)   # una restricción por cada ciudad
)

# Combinamos las dos restricciones y escalamos con P.
# r1 + r2 garantiza que la solución codifique una permutación válida.
restricciones = P * (r1 + r2)

# ── HAMILTONIANO ──────────────────────────────────────────────────────────────
H = objetivo + restricciones

# Verificamos que el Hamiltoniano tiene exactamente n×n = 16 bits.
print(f"Hamiltoniano TSP creado con {H.N} bits (esperado: {n*n})")

# ── SOLVER ────────────────────────────────────────────────────────────────────
# El espacio de búsqueda es 2^16 = 65536 configuraciones.
# Solo n! = 24 son permutaciones válidas; el resto son infactibles.
# Aumentamos number_iterations para explorar mejor este espacio más grande.
number_runs = 16
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=2000,    # más iteraciones para problema de 16 bits
    scaling_bit_precision=48
)
solution_list = solver.minimize(H)
mejor  = solution_list.min_solution
config = mejor.configuration   # dict con 16 bits

# ── DECODIFICAR RUTA ──────────────────────────────────────────────────────────
# Recorremos cada posición p y buscamos qué ciudad tiene x_{c,p} = 1.
# Si la solución es válida, cada posición tendrá exactamente una ciudad asignada.
ruta_indices = []
for p in range(n):
    ciudad_en_p = None
    for c in range(n):
        if config[idx(c, p)] == 1:
            ciudad_en_p = c   # ciudad c está en la posición p
    ruta_indices.append(ciudad_en_p)

# Convertimos índices numéricos a nombres de ciudades.
ruta = [ciudades[c] if c is not None else "?" for c in ruta_indices]

# Validamos la ruta: debe contener las n ciudades sin repetición ni huecos.
ruta_valida = all(c is not None for c in ruta_indices) and len(set(ruta_indices)) == n

# Calculamos la distancia real del ciclo solo si la ruta es válida.
distancia_total = 0
if ruta_valida:
    for p in range(n):
        origen  = ruta_indices[p]
        destino = ruta_indices[(p + 1) % n]   # el último nodo vuelve al primero
        distancia_total += distancias[origen][destino]

print("\nRESULTADO TSP")
print("=" * 60)
# Mostramos la ruta como ciclo: última ciudad vuelve a la primera.
print("Ruta:", " → ".join(ruta + [ruta[0]]))
print(f"Ruta válida      : {'sí ✓' if ruta_valida else 'no ✗'}")
print(f"Distancia total  : {distancia_total}")
# Penalización = 0 confirma que las dos restricciones (posición y ciudad) se cumplen.
print(f"Penalización     : {restricciones.compute(config)}")
# H.compute(config) devuelve la energía real del problema (no la escalada internamente).
print(f"Energía H        : {H.compute(config)}")
print(f"Frecuencia       : {int(mejor.frequency)} de {number_runs} runs")

# ── MATRIZ CIUDAD-POSICIÓN ────────────────────────────────────────────────────
# La matriz x_{ciudad, posición} debe ser una matriz de permutación:
# exactamente un 1 por fila y por columna si la solución es válida.
# Cualquier fila o columna con más o menos de un 1 indica solución infactible.
print("\nMatriz x_{ciudad, posición}:")
print("        " + "  ".join(f"pos{p}" for p in range(n)))
for c in range(n):
    fila = [str(config[idx(c, p)]) for p in range(n)]
    print(f"  {ciudades[c]:>3}:  " + "     ".join(fila))