#!/usr/bin/env python3
"""
MAXIMUM CUT PROBLEM - GRAFO DE N NODOS
=======================================

Script interactivo que pide al usuario el número de nodos, el tipo de grafo
y resuelve el problema Maximum Cut mediante Simulated Annealing (D-Wave Ocean).

El modelo QUBO se escribe de forma SIMBÓLICA con dimod (igual que en los
ejercicios 1-6): una variable binaria por nodo y un término por arista.

Tipos de grafo:
  1. Completo (Kn) - todos conectados con todos (didáctico)
  2. Aleatorio (Erdős-Rényi) - cada arista existe con probabilidad p
  3. Regular - cada nodo tiene exactamente k vecinos
"""

import os
import time
import numpy as np
import dimod
from dwave.samplers import SimulatedAnnealingSampler
import matplotlib.pyplot as plt
import networkx as nx

print("=" * 70)
print("   MAXIMUM CUT - GRAFO DE N NODOS")
print("=" * 70)
print()

# =============================================================================
# ENTRADA DEL USUARIO
# =============================================================================

# --- Número de nodos ---
DEFAULT_NODOS = 10    # Valor por defecto
while True:
    try:
        entrada = input(f"Número de nodos (3-100, por defecto {DEFAULT_NODOS}): ").strip()
        if entrada == "":
            num_nodos = DEFAULT_NODOS
            break
        num_nodos = int(entrada)
        if num_nodos < 3:
            print("El mínimo son 3 nodos.")
            continue
        if num_nodos > 100:
            print("Más de 100 nodos puede tardar mucho. ¿Seguro? (s/n): ", end="")
            if input().strip().lower() != "s":
                continue
        break
    except ValueError:
        print("Introduce un número entero válido.")
print(f"   Usando {num_nodos} nodos")

# --- Tipo de grafo: Erdős-Rényi (fijo, sin preguntar al usuario) ---
tipo_grafo = 2
prob = 0.5
param_extra = f"p={prob}"

# Ajustar parámetros según tamaño (siempre 10 lotes = progreso de 10 en 10%)
if num_nodos <= 10:
    num_reads = 1000
elif num_nodos <= 20:
    num_reads = 2000
elif num_nodos <= 40:
    num_reads = 5000
else:
    num_reads = 10000

batch_size = num_reads // 10

num_batches = num_reads // batch_size

print()
print(f"Configuración automática: {num_reads} lecturas en {num_batches} lotes de {batch_size}")
print()

# =============================================================================
# PASO 1: CREACIÓN DEL GRAFO
# =============================================================================
nombres_tipo = {
    1: "Completo (Kn)",
    2: f"Aleatorio Erdős-Rényi ({param_extra})",
    3: f"Regular ({param_extra})",
    4: "Manual (grados personalizados)",
    5: f"Small-World Watts-Strogatz ({param_extra})",
    6: f"Scale-Free Barabási-Albert ({param_extra})",
    7: f"Comunidades ({param_extra})",
}
nombre_tipo = nombres_tipo[tipo_grafo]
print(f"PASO 1: Creando grafo {nombre_tipo}...")
print("-" * 50)

if tipo_grafo == 1:
    G = nx.complete_graph(num_nodos)
elif tipo_grafo == 2:
    # Generar hasta obtener un grafo conexo
    for intento in range(100):
        G = nx.erdos_renyi_graph(num_nodos, prob)
        if nx.is_connected(G):
            break
    else:
        print("   Aviso: el grafo no es conexo. Puede haber nodos aislados.")
elif tipo_grafo == 3:
    G = nx.random_regular_graph(k_reg, num_nodos)
elif tipo_grafo == 4:
    # Generar grafo con grados exactos usando Havel-Hakimi (determinista, grados exactos)
    G = nx.havel_hakimi_graph(secuencia_grados)
    if not nx.is_connected(G):
        print("   Aviso: el grafo no es conexo (puede haber nodos aislados).")
    print(f"   Grados solicitados: [{resumen_grados}]")
    grados_reales = ", ".join(f"{n}:{d}" for n, d in G.degree())
    print(f"   Grados obtenidos:   [{grados_reales}]")
elif tipo_grafo == 5:
    G = nx.watts_strogatz_graph(num_nodos, k_sw, p_sw)
elif tipo_grafo == 6:
    G = nx.barabasi_albert_graph(num_nodos, m_ba)
elif tipo_grafo == 7:
    # Crear comunidades de tamaños aproximadamente iguales
    tamano_base = num_nodos // n_comunidades
    resto = num_nodos % n_comunidades
    tamanos = [tamano_base + (1 if i < resto else 0) for i in range(n_comunidades)]
    # Matriz de probabilidades: p_intra en diagonal, p_inter fuera
    probs = [[p_intra if i == j else p_inter for j in range(n_comunidades)]
             for i in range(n_comunidades)]
    G = nx.stochastic_block_model(tamanos, probs)
    # Guardar las comunidades para mostrar
    comunidades_nodos = []
    inicio = 0
    for t in tamanos:
        comunidades_nodos.append(list(range(inicio, inicio + t)))
        inicio += t
    print(f"   Comunidades: {comunidades_nodos}")

num_aristas = len(G.edges())

# Grado medio real
grados = [d for _, d in G.degree()]
grado_medio = np.mean(grados)

print(f"   Tipo: {nombre_tipo}")
print(f"   Nodos: {num_nodos}")
print(f"   Aristas: {num_aristas}" + (f"  (Kn tendría {num_nodos*(num_nodos-1)//2})" if tipo_grafo != 1 else f"  (n*(n-1)/2 = {num_nodos}*{num_nodos-1}/2)"))
print(f"   Grado medio: {grado_medio:.1f}  (min={min(grados)}, max={max(grados)})")
print(f"   Densidad: {nx.density(G)*100:.1f}%")
print(f"   Qubits simulados: {num_nodos}  (1 qubit por nodo)")
print(f"   Espacio de búsqueda: 2^{num_nodos} = {2**num_nodos:,} configuraciones")
print(f"   Reads (muestras SA): {num_reads}  (cubren {num_reads/2**num_nodos*100:.4f}% del espacio)")
print()

# =============================================================================
# PASO 2: FORMULACIÓN QUBO
# =============================================================================
print("PASO 2: Construyendo el modelo QUBO (simbólico)...")
print("-" * 50)

start_time = time.time()

# Una variable binaria por nodo: x[i] = 0 → grupo A, x[i] = 1 → grupo B
x = [dimod.Binary(i) for i in range(num_nodos)]

# Arista (i, j) cortada ⇔ x_i + x_j − 2·x_i·x_j = 1  (XOR)
# Maximizar aristas cortadas = minimizar el negativo
H = -sum(x[i] + x[j] - 2 * x[i] * x[j] for i, j in G.edges())

qubo_time = time.time() - start_time

terminos_lineales = H.num_variables
terminos_cuadraticos = len(H.quadratic)

print(f"   Términos lineales (uno por nodo): {terminos_lineales}")
print(f"   Términos cuadráticos (uno por arista): {terminos_cuadraticos}")
print(f"   Construida en {qubo_time:.3f}s")
print()

# =============================================================================
# PASO 3: RESOLUCIÓN CON SIMULATED ANNEALING
# =============================================================================
print("PASO 3: Simulated Annealing...")
print("-" * 50)

titulo_grafo = f"K{num_nodos}" if tipo_grafo == 1 else f"{num_nodos} nodos, {nombre_tipo}"

start_time = time.time()
sampler = SimulatedAnnealingSampler()      # versión rápida (C++) de dwave-samplers
all_responses = []
evoluciones = []
sin_mejora = 0  # Contador de lotes consecutivos sin mejora
mejor_energia_global = float('inf')

for batch in range(num_batches):
    batch_start = time.time()
    batch_response = sampler.sample(H, num_reads=batch_size)
    batch_time = time.time() - batch_start
    all_responses.append(batch_response)

    completado = (batch + 1) * batch_size
    porcentaje = (batch + 1) / num_batches * 100
    mejor_batch = batch_response.first
    mejor_energia_batch = mejor_batch.energy
    grupo_a = sorted([n for n in range(num_nodos) if mejor_batch.sample[n] == 0])
    grupo_b = sorted([n for n in range(num_nodos) if mejor_batch.sample[n] == 1])
    barra = "█" * int(porcentaje // 10) + "░" * (10 - int(porcentaje // 10))
    print(f"   [{barra}] {porcentaje:5.1f}%  ({completado:,}/{num_reads:,})  "
          f"E={mejor_energia_batch:.0f}  ({batch_time:.1f}s)", flush=True)
    print(f"            A={grupo_a}")
    print(f"            B={grupo_b}")

    # Mejor global acumulada hasta este lote
    global_response = dimod.concatenate(all_responses)
    mejor_global = global_response.first
    sample = dict(mejor_global.sample)
    corte_lote = sum(1 for i, j in G.edges() if sample[i] != sample[j])
    evoluciones.append({
        'porcentaje': int(porcentaje),
        'sample': sample,
        'energia': mejor_global.energy,
        'corte': corte_lote,
    })

    # Detectar convergencia
    if mejor_global.energy < mejor_energia_global:
        mejor_energia_global = mejor_global.energy
        sin_mejora = 0
    else:
        sin_mejora += 1

    # Parada anticipada: 3 lotes seguidos sin mejora
    if sin_mejora >= 3:
        print(f"\n   [CONVERGENCIA] Sin mejora en {sin_mejora} lotes consecutivos. Parando.")
        print(f"   Reads usados: {completado} de {num_reads} ({porcentaje:.0f}%)")
        break

solving_time = time.time() - start_time

response = dimod.concatenate(all_responses)
mejor_solucion = response.first.sample
energia_minima = response.first.energy

print()
reads_usados = len(all_responses) * batch_size
lotes_usados = len(all_responses)
parada_anticipada = lotes_usados < num_batches

print(f"   Tiempo total: {solving_time:.2f}s")
if parada_anticipada:
    print(f"   Parada anticipada: {lotes_usados}/{num_batches} lotes ({reads_usados}/{num_reads} reads)")
print(f"   Promedio por lote: {solving_time/lotes_usados:.2f}s  |  "
      f"Por lectura: {solving_time/reads_usados*1000:.2f}ms")
print()

# =============================================================================
# PASO 4: ANÁLISIS DE RESULTADOS
# =============================================================================
print("PASO 4: Resultados...")
print("-" * 50)

particion_0 = sorted([n for n in G.nodes() if mejor_solucion[n] == 0])
particion_1 = sorted([n for n in G.nodes() if mejor_solucion[n] == 1])

aristas_cortadas = [(i, j) for i, j in G.edges() if mejor_solucion[i] != mejor_solucion[j]]
tamano_corte = len(aristas_cortadas)

# Corte teórico máximo
if tipo_grafo == 1:
    # Grafo completo: fórmula exacta floor(n/2)*ceil(n/2)
    corte_max = (num_nodos // 2) * ((num_nodos + 1) // 2)
else:
    # Grafos no completos: el máximo teórico es el total de aristas
    # (inalcanzable en general, pero sirve como referencia)
    corte_max = num_aristas

calidad = tamano_corte / corte_max * 100 if corte_max > 0 else 0

print(f"   Partición A: {len(particion_0)} nodos -> {particion_0}")
print(f"   Partición B: {len(particion_1)} nodos -> {particion_1}")
print(f"   Aristas cortadas: {tamano_corte} de {num_aristas} ({tamano_corte/num_aristas*100:.1f}%)")
if tipo_grafo == 1:
    print(f"   Corte teórico máximo: {corte_max} (exacto para Kn)")
else:
    print(f"   Corte máximo posible: {corte_max} (cota superior = total aristas)")
print(f"   Calidad: {calidad:.2f}%")
print()

# Estadísticas del sampler
todas_energias = [s.energy for s in response.data()]
ocurrencias_mejor = sum(1 for e in todas_energias if e == energia_minima)

print("   Estadísticas del sampler:")
print(f"      Energía mínima: {min(todas_energias):.0f}")
print(f"      Energía máxima: {max(todas_energias):.0f}")
print(f"      Energía promedio: {np.mean(todas_energias):.1f}")
print(f"      Desviación estándar: {np.std(todas_energias):.1f}")
print(f"      Veces solución óptima: {ocurrencias_mejor}/{reads_usados} ({ocurrencias_mejor/reads_usados*100:.1f}%)")
print()

# =============================================================================
# RESUMEN
# =============================================================================
print("=" * 70)
print("   RESUMEN")
print("=" * 70)

if calidad == 100:
    estado = "ÓPTIMA"
elif calidad >= 95:
    estado = "EXCELENTE (>=95%)"
elif calidad >= 90:
    estado = "BUENA (>=90%)"
else:
    estado = "ACEPTABLE"

print(f"   Problema: Maximum Cut, {nombre_tipo}, {num_nodos} nodos")
print(f"   Nodos: {num_nodos}  |  Aristas: {num_aristas}  |  Qubits simulados: {num_nodos}")
if parada_anticipada:
    print(f"   Reads: {reads_usados}/{num_reads} (parada anticipada)  |  Cobertura: {reads_usados/2**num_nodos*100:.4f}%")
else:
    print(f"   Reads: {num_reads}  |  Cobertura del espacio: {num_reads/2**num_nodos*100:.4f}%")
print(f"   Corte: {tamano_corte}/{corte_max}  |  Calidad: {calidad:.1f}%  |  {estado}")
print(f"   Particiones: {len(particion_0)} vs {len(particion_1)}")
print(f"   Tiempo QUBO: {qubo_time:.3f}s  |  Tiempo SA: {solving_time:.2f}s  |  "
      f"Total: {qubo_time + solving_time:.2f}s")
print("=" * 70)
print()

# =============================================================================
# VISUALIZACIÓN: Resumen (izquierda) + Evolución 10%-100% (derecha)
# =============================================================================
print("Generando gráfico de evolución...")

pos = nx.circular_layout(G) if tipo_grafo == 1 else nx.spring_layout(G, seed=42)
node_size = max(150, 600 - num_nodos * 8)
font_size = max(6, 11 - num_nodos // 8)

# Layout: 1 columna izquierda para resumen + 2 columnas para soluciones
fig = plt.figure(figsize=(16, 9))
gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1.7], hspace=0.2, wspace=0.3)

# --- PANEL IZQUIERDO: RESUMEN ---
ax_resumen = fig.add_subplot(gs[0, 0])
ax_resumen.axis('off')

reads_str = f"{reads_usados}/{num_reads}" if parada_anticipada else f"{reads_usados}"
parada_str = f"\nPARADA ANTICIPADA\n(convergencia en lote {lotes_usados})\n\n" if parada_anticipada else "\n"

tipos_cortos = {
    1: f"K{num_nodos}",
    2: f"E-R {param_extra}",
    3: f"Reg {param_extra}",
    4: "Manual",
    5: f"S-W {param_extra}",
    6: f"B-A {param_extra}",
    7: f"Comunidades",
}
tipo_corto = tipos_cortos[tipo_grafo]

resumen_texto = (
    f"MAXIMUM CUT\n"
    f"{tipo_corto} ({num_nodos} nodos)\n"
    f"{'=' * 30}\n\n"
    f"Tipo: {nombre_tipo}\n"
    f"Nodos: {num_nodos}\n"
    f"Aristas: {num_aristas}\n"
    f"Densidad: {nx.density(G)*100:.1f}%\n"
    f"Qubits simulados: {num_nodos}\n"
    f"Espacio: 2^{num_nodos} = {2**num_nodos:,}\n\n"
    f"Reads: {reads_str}\n"
    f"Lotes: {lotes_usados}/{num_batches} x {batch_size}\n"
    f"Cobertura: {reads_usados/2**num_nodos*100:.4f}%\n"
    f"{parada_str}"
    f"{'=' * 30}\n"
    f"RESULTADO FINAL\n"
    f"{'=' * 30}\n\n"
    f"Corte: {tamano_corte} / {corte_max}\n"
    f"Calidad: {calidad:.1f}%  ({estado})\n"
    f"Energia: {energia_minima:.0f}\n\n"
    f"Particion A: {len(particion_0)} nodos\n"
    f"Particion B: {len(particion_1)} nodos\n\n"
    f"Tiempo QUBO: {qubo_time:.3f}s\n"
    f"Tiempo SA: {solving_time:.2f}s\n"
    f"Total: {qubo_time + solving_time:.2f}s\n\n"
    f"{'=' * 30}\n"
    f"ESTADISTICAS\n"
    f"{'=' * 30}\n\n"
    f"E min: {min(todas_energias):.0f}\n"
    f"E max: {max(todas_energias):.0f}\n"
    f"E media: {np.mean(todas_energias):.1f}\n"
    f"Desv. std: {np.std(todas_energias):.1f}\n"
    f"Tasa exito: {ocurrencias_mejor}/{reads_usados}\n"
    f"({ocurrencias_mejor/reads_usados*100:.1f}%)"
)

ax_resumen.text(0.05, 0.98, resumen_texto,
                transform=ax_resumen.transAxes, verticalalignment='top',
                fontfamily='monospace', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.9))

# --- PANELES DERECHOS: 10 soluciones de peor a mejor energía ---
# Recopilar una solución representativa por cada tamaño de partición (= nivel de energía)
# En Kn, particiones del mismo tamaño siempre dan el mismo corte (a*b)
por_tamano = {}
for s in response.data():
    sample_dict = dict(s.sample)
    n_a = sum(1 for v in range(num_nodos) if sample_dict[v] == 0)
    n_b = num_nodos - n_a
    tamano = (min(n_a, n_b), max(n_a, n_b))  # Normalizar (ej. 3v6 = 6v3)
    if tamano not in por_tamano:
        por_tamano[tamano] = {
            'sample': sample_dict,
            'energia': s.energy,
            'tamano': tamano,
        }

# Seleccionar la mejor solución (menor energía)
niveles = sorted(por_tamano.values(), key=lambda x: x['energia'])
seleccion = niveles[:1]

print(f"   Niveles de energía distintos: {len(niveles)}")
print(f"   Mostrando mejor partición: ", end="")
print(" → ".join(f"{s['tamano'][0]}v{s['tamano'][1]}" for s in seleccion))

for idx, sol in enumerate(seleccion):
    col = idx + 1  # columna 0 es el resumen

    ax = fig.add_subplot(gs[0, col])

    sample = sol['sample']
    energia_sol = sol['energia']
    corte_sol = sum(1 for i, j in G.edges() if sample[i] != sample[j])

    # Colores de partición
    colores = ['#5B9BD5' if sample[n] == 0 else '#FF6B6B' for n in G.nodes()]

    # Aristas cortadas
    aristas_corte = [(i, j) for i, j in G.edges() if sample[i] != sample[j]]

    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores,
                           node_size=node_size, edgecolors='black', linewidths=0.5)

    # Dibujar todas las aristas (gris) y las cortadas (rojo)
    aristas_no_corte = [(i, j) for i, j in G.edges() if sample[i] == sample[j]]
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_no_corte,
                           edge_color='#CCCCCC', width=0.4, alpha=0.3)
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_corte,
                           edge_color='red', width=0.6, alpha=0.5)

    # Etiquetas solo si caben
    if num_nodos <= 30:
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=font_size, font_weight='bold')

    n_a = sum(1 for n in G.nodes() if sample[n] == 0)
    n_b = sum(1 for n in G.nodes() if sample[n] == 1)

    # Título con tamaño de partición y energía
    ax.set_title(f"{sol['tamano'][0]}v{sol['tamano'][1]}  E={energia_sol:.0f}  Corte={corte_sol}\n"
                 f"A:{n_a}  B:{n_b}",
                 fontsize=8, fontweight='bold')

    # Marcar si es solución óptima
    if corte_sol == corte_max:
        ax.patch.set_facecolor('#e6ffe6')
        ax.patch.set_alpha(0.3)


plt.suptitle(f"Maximum Cut {titulo_grafo} - Mejor solución",
             fontsize=16, fontweight='bold', y=0.97)

directorio_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'png')
os.makedirs(directorio_png, exist_ok=True)
nombre_archivo = os.path.join(directorio_png, f"max_cut_{num_nodos}_nodos_resultado.png")
plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
print(f"Gráfico guardado: {nombre_archivo}")
plt.show(block=False)

input("Pulsa Enter para cerrar el gráfico...")
plt.close('all')
