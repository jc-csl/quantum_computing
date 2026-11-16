"""
Ejercicio 6 (ampliación) · Max-Cut con N nodos                 (N variables)
============================================================================
El mismo problema del ejercicio 5, pero con una red aleatoria del tamaño
que tú elijas. Sirve para ver qué pasa cuando el problema crece:
    · el número de combinaciones posibles es 2^N (crece muchísimo)
    · el modelo QUBO solo tiene N variables y una interacción por arista

Necesita:  pip install networkx matplotlib
Ejecutar:  python ejercicio6_maxcut_n_nodos.py
"""
import time
import dimod
import networkx as nx
import matplotlib.pyplot as plt
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS: pedir N y crear una red aleatoria ─────────────────────────
texto = input("Número de nodos (3-60, Enter = 12): ").strip()
n = int(texto) if texto else 12
G = nx.erdos_renyi_graph(n, 0.5, seed=1)   # cada conexión existe con prob. 0,5
print(f"Red: {n} nodos, {G.number_of_edges()} aristas")
print(f"Combinaciones posibles: 2^{n} = {2**n:,}")

# ── 2. VARIABLES: una por nodo (0 → grupo A, 1 → grupo B) ───────────────
x = [dimod.Binary(i) for i in range(n)]

# ── 3. OBJETIVO: −(aristas cortadas), igual que en el ejercicio 5 ───────
H = 0
for i, j in G.edges():
    H = H - (x[i] + x[j] - 2 * x[i] * x[j])

# ── 6. RESOLVER (y medir el tiempo) ─────────────────────────────────────
inicio = time.time()
resultado = SimulatedAnnealingSampler().sample(H, num_reads=100, seed=42)
segundos = time.time() - inicio

# ── 7. INTERPRETAR ──────────────────────────────────────────────────────
mejor = resultado.first
cfg = mejor.sample
corte = int(-mejor.energy)
print(f"\nMejor corte encontrado: {corte} de {G.number_of_edges()} aristas")
print(f"Tiempo: {segundos:.2f} s para 100 intentos (num_reads)")

# ¿Cuántos de los 100 intentos llegaron a ese mismo corte?
energias = resultado.record.energy
veces = int(sum(resultado.record.num_occurrences[energias == mejor.energy]))
print(f"Intentos que llegaron al mejor corte: {veces} de 100")

# Con pocos nodos podemos comprobar el óptimo por fuerza bruta
if n <= 16:
    optimo = int(-dimod.ExactSolver().sample(H).first.energy)
    print(f"Óptimo real (fuerza bruta): {optimo}  →  ",
          "¡encontrado!" if optimo == corte else "no alcanzado")

# ── Dibujo: azul = grupo A, naranja = grupo B, rojo = arista cortada ────
colores = ["#4c5fd5" if cfg[i] == 0 else "#f08c00" for i in G.nodes()]
cortadas = [(i, j) for i, j in G.edges() if cfg[i] != cfg[j]]
pos = nx.spring_layout(G, seed=7)
nx.draw_networkx_edges(G, pos, edge_color="#cccccc")
nx.draw_networkx_edges(G, pos, edgelist=cortadas, edge_color="#e03131")
nx.draw_networkx_nodes(G, pos, node_color=colores)
nx.draw_networkx_labels(G, pos, font_color="white")
plt.title(f"Max-Cut {n} nodos: {corte}/{G.number_of_edges()} aristas cortadas")
plt.axis("off")
plt.show()
