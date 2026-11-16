# ── SECCIÓN 6: Código Python completo y comentado ──────────────────────────────
# Ejercicio 4 — Max-Cut con DADK 3.11
#
# OBJETIVO DEL EJERCICIO:
# Dado un grafo no dirigido, dividir sus nodos en dos grupos (A y B) de modo
# que se maximice el número de aristas que cruzan la frontera entre grupos
# (aristas "cortadas"). Max-Cut es NP-completo en grafos generales.
#

try:
    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU
    print("[Usando Fujitsu DADK]")
except ImportError:  # sin DADK: simulador didáctico con la misma API
    from mini_qubo import BinPol, Term, QUBOSolverCPU
    print("[DADK no instalado: usando mini_qubo]")

# ── DATOS ─────────────────────────────────────────────────────────────────────
nodos = [0, 1, 2, 3, 4, 5, 6]   # 7 nodos del grafo

# 10 aristas no dirigidas. El grafo tiene ciclo impar 0-1-4-5-2-0 (longitud 5)
# → NO es bipartito → no es posible cortar las 10 aristas (máximo teórico = 9).
aristas = [
    (0, 1), (0, 2),           # nodo 0 conecta con 1 y 2
    (1, 3), (1, 4),           # nodo 1 conecta con 3 y 4
    (2, 3), (2, 5),           # nodo 2 conecta con 3 y 5
    (3, 6),                   # nodo 3 conecta con 6
    (4, 5), (4, 6),           # nodo 4 conecta con 5 y 6
    (5, 6),                   # nodo 5 conecta con 6
]

# ── VARIABLES BINARIAS ────────────────────────────────────────────────────────
# x[i] = 0 → nodo i pertenece al GRUPO A
# x[i] = 1 → nodo i pertenece al GRUPO B
# No hay penalizaciones; cualquier asignación binaria es factible.
x = [Term(1, i) for i in nodos]

# ── OBJETIVO ──────────────────────────────────────────────────────────────────
# Para cada arista (i, j), la expresión  x_i + x_j − 2·x_i·x_j  vale:
#   i∈A(0), j∈A(0):  0 + 0 − 0 = 0  → arista no cortada (mismo grupo)
#   i∈A(0), j∈B(1):  0 + 1 − 0 = 1  → arista cortada    (grupos distintos) ✓
#   i∈B(1), j∈A(0):  1 + 0 − 0 = 1  → arista cortada    (grupos distintos) ✓
#   i∈B(1), j∈B(1):  1 + 1 − 2 = 0  → arista no cortada (mismo grupo)
#
# Equivale a XOR lógico: la arista se corta si y solo si los bits de sus extremos difieren.
#
# Queremos MAXIMIZAR el número de aristas cortadas → MINIMIZAMOS el negativo.
corte = BinPol.sum(x[i] + x[j] - 2 * x[i] * x[j] for i, j in aristas)
H = -corte   # minimizar(−corte) ⟺ maximizar(corte)

print(f"Hamiltoniano Max-Cut creado con {H.N} bits")
print(f"Número de aristas: {len(aristas)}  |  Máximo corte teórico: {len(aristas) - 1}")

# ── SOLVER ────────────────────────────────────────────────────────────────────
# 7 bits → 2^7 = 128 configuraciones posibles.
# Sin restricciones, cualquier configuración es válida; solo varía el corte.
number_runs = 12
solver = QUBOSolverCPU(
    number_runs=number_runs,
    number_iterations=800,   # suficiente para explorar 128 combinaciones
    scaling_bit_precision=48
)
solution_list = solver.minimize(H)
mejor  = solution_list.min_solution
config = mejor.configuration   # dict {bit: 0_o_1} con la partición óptima

# ── INTERPRETACIÓN DEL RESULTADO ──────────────────────────────────────────────
# Separamos los nodos en grupo A (bit=0) y grupo B (bit=1).
grupo_A          = [i for i in nodos if config[i] == 0]
grupo_B          = [i for i in nodos if config[i] == 1]

# Una arista está cortada cuando sus dos extremos pertenecen a grupos distintos.
aristas_cortadas = [(i, j) for i, j in aristas if config[i] != config[j]]

print("\nRESULTADO MAX-CUT")
print("=" * 60)
print(f"Grupo A: nodos {grupo_A}")
print(f"Grupo B: nodos {grupo_B}")
print(f"Aristas cortadas          : {aristas_cortadas}")
print(f"Número de aristas cortadas: {len(aristas_cortadas)} de {len(aristas)}")

# H.compute(config) devuelve la energía real (= −número de aristas cortadas).
print(f"Energía H                 : {H.compute(config)}  (= −{len(aristas_cortadas)})")
print(f"Frecuencia                : {int(mejor.frequency)} de {number_runs} runs")

# ── TABLA DE SOLUCIONES ────────────────────────────────────────────────────────
# Nota sobre simetría: los pares complementarios (invertir todos los bits)
# producen exactamente el mismo corte → verás duplicados con energía idéntica.
print("\nSoluciones encontradas:")
print(f"{'bits':>8} {'grupo A':>16} {'grupo B':>16} {'corte':>6} {'H':>8} {'freq':>6}")
print("-" * 66)
for sol in solution_list.solutions[:10]:
    cfg  = sol.configuration
    gA   = [i for i in nodos if cfg[i] == 0]
    gB   = [i for i in nodos if cfg[i] == 1]
    cut  = sum(1 for i, j in aristas if cfg[i] != cfg[j])
    bits = ''.join(str(cfg[i]) for i in nodos)
    print(f"{bits:>8} {str(gA):>16} {str(gB):>16} {cut:>6} {H.compute(sol.configuration):>8.1f} {int(sol.frequency):>6}")

# ── VISUALIZACIÓN (opcional: requiere matplotlib y networkx) ──
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    
    # ── Construimos el grafo con la misma estructura que usó el solver ──────────────
    G = nx.Graph()
    G.add_nodes_from(nodos)          # añadimos los nodos definidos en el ejercicio
    G.add_edges_from(aristas)        # añadimos todas las aristas del grafo
    pos = nx.spring_layout(G, seed=42)  # posición fija (seed) para reproducibilidad
    
    # ── Colores y etiquetas según la partición obtenida ────────────────────────────
    # config[i] == 0 → grupo A (azul);  config[i] == 1 → grupo B (naranja)
    colores = ["#4C9BE8" if config[i] == 0 else "#E8734C" for i in nodos]
    etiquetas = {i: f"{i}\n({'A' if config[i]==0 else 'B'})" for i in nodos}
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    
    # ── Panel izquierdo: grafo original sin colorear ───────────────────────────────
    nx.draw(G, pos, ax=axes[0], with_labels=True, node_color="lightgray",
            node_size=800, font_size=12, edge_color="gray", width=2)
    axes[0].set_title("Grafo original")
    
    # ── Panel derecho: partición Max-Cut ──────────────────────────────────────────
    # Identificamos qué aristas cruzan la frontera A/B (aristas cortadas)
    aristas_cortadas_set = set(map(frozenset, aristas_cortadas))
    
    # Aristas cortadas → rojo;  aristas internas → gris
    colores_aristas = ["#E84C4C" if frozenset([u, v]) in aristas_cortadas_set else "#AAAAAA"
                       for u, v in G.edges()]
    # Aristas cortadas más gruesas para resaltarlas visualmente
    anchos_aristas = [3 if frozenset([u, v]) in aristas_cortadas_set else 1.5
                      for u, v in G.edges()]
    
    nx.draw(G, pos, ax=axes[1], labels=etiquetas, node_color=colores,
            node_size=900, font_size=10, edge_color=colores_aristas, width=anchos_aristas)
    axes[1].set_title(f"Max-Cut  |  corte = {len(aristas_cortadas)}  |  azul=A  naranja=B")
    
    plt.tight_layout()
    plt.show()
except ImportError:
    print("Instala matplotlib y networkx para ver el grafo")
