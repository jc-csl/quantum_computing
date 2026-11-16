# 6 · Glosario

Ordenado por bloques. Las definiciones están simplificadas para el nivel del ciclo.

## A. Fundamentos cuánticos

| Término | Definición |
|---|---|
| **Computación cuántica** | Paradigma de computación que usa principios de la mecánica cuántica (superposición, entrelazamiento, interferencia) para resolver ciertos problemas que son ineficientes o imposibles para ordenadores clásicos. |
| **Qubit (cúbit)** | Unidad básica de información cuántica. Puede valer 0, 1 o una superposición de ambos con ciertas amplitudes de probabilidad. |
| **Amplitud de probabilidad** | Número (α, β) asociado a cada estado. Su cuadrado es la probabilidad de obtener ese estado al medir. |
| **Superposición** | Capacidad de un sistema cuántico de estar en varios estados a la vez. n qubits → 2ⁿ estados simultáneos. |
| **Esfera de Bloch** | Representación de un qubit como un punto en una esfera de radio 1: polo norte = \|0⟩, polo sur = \|1⟩. |
| **Medición** | Al medir, la superposición colapsa a un valor clásico (0 o 1) con cierta probabilidad. Destruye la superposición. |
| **Interferencia** | Las amplitudes se combinan como ondas: se refuerzan (constructiva) o se cancelan (destructiva). Permite favorecer la respuesta correcta. |
| **Entrelazamiento** | Correlación cuántica entre qubits: el estado de uno depende del otro aunque estén lejos. |
| **Decoherencia** | Pérdida del comportamiento cuántico por medición o por ruido del entorno. Principal enemigo del hardware cuántico. |
| **Túnel cuántico** | Una partícula atraviesa una barrera de energía que clásicamente no podría superar. Ayuda a salir de mínimos locales. |
| **Qubit físico / lógico** | Físico: el qubit real del chip. Lógico: qubit fiable formado por varios físicos con corrección de errores. |
| **NISQ** | *Noisy Intermediate-Scale Quantum*: era actual de ordenadores cuánticos con ruido y tamaño medio. |
| **Ventaja cuántica** | Resolver un problema mejor, más rápido o más barato que cualquier método clásico conocido. |
| **QPU** | *Quantum Processing Unit*: procesador cuántico. |

## B. Annealing y hardware

| Término | Definición |
|---|---|
| **Quantum Annealing** | Computación cuántica especializada en optimización: busca el mínimo global de un paisaje de energía usando superposición y efecto túnel. |
| **Simulated Annealing** | Algoritmo clásico que imita el recocido de metales: acepta empeorar con una probabilidad que depende de la temperatura. |
| **Digital Annealer (Fujitsu)** | Hardware digital CMOS inspirado en el annealing. Funciona a temperatura ambiente, hasta 100.000 variables conectadas todas con todas. |
| **D-Wave** | Empresa canadiense pionera en ordenadores cuánticos de annealing (Advantage: 5.000+ qubits; Advantage2: 4.400+ qubits). |
| **Leap** | Servicio en la nube de D-Wave para acceder a sus QPU y solvers híbridos. |
| **Topología (Pegasus / Zephyr)** | Forma en que se conectan los qubits en un chip D-Wave (Zephyr: cada qubit con 20 vecinos). |
| **Embedding** | Representar una variable del problema con varios qubits físicos encadenados cuando el chip no tiene las conexiones necesarias. |
| **Paisaje de energía** | Representación de todas las soluciones con su energía: valles = buenas soluciones, picos = malas. |
| **Mínimo local / global** | Local: valle que no es el más profundo. Global: la mejor solución posible. |
| **Temperatura (T)** | Parámetro del annealing: alta → explora (acepta empeorar); baja → afina. |
| **Iteraciones** | Pasos de búsqueda dentro de una ejecución. |
| **Runs** | Ejecuciones independientes del solver sobre el mismo problema. |
| **Frecuencia** | Número de runs que acabaron en la misma solución. |
| **Híbrido** | Trabajo combinado: CPU clásica prepara/ajusta y QPU busca soluciones. |
| **QAOA / VQE** | Algoritmos híbridos para ordenadores de puertas: optimización (QAOA) y química (VQE). |

## C. Modelado QUBO

| Término | Definición |
|---|---|
| **QUBO** | *Quadratic Unconstrained Binary Optimization*: minimizar una función cuadrática de variables binarias; las restricciones se meten como penalizaciones. |
| **Modelo Ising** | Equivalente a QUBO con variables {−1, +1}. |
| **Variable binaria** | Decisión SÍ/NO: 0 o 1. Cumple x² = x. |
| **Función objetivo** | Expresión de lo que se quiere optimizar (coste, distancia, −beneficio…). |
| **Penalización** | Término P·(restricción)² que suma energía a las soluciones que no cumplen. |
| **P** | Peso de la penalización. Debe superar el máximo beneficio obtenible incumpliendo. |
| **Hamiltoniano (H)** | Función de energía total: objetivo + penalizaciones. |
| **Energía** | Valor de H en una combinación. Menor = mejor. |
| **Matriz Q** | Representación de H: diagonal = términos lineales; fuera de la diagonal = interacciones xᵢxⱼ. |
| **Offset / constante** | Término sin variables. No cambia la solución óptima, solo desplaza las energías. |
| **Variable de holgura (slack)** | Bits extra que convierten una desigualdad (≤) en igualdad (=). |
| **Factible** | Solución que cumple todas las restricciones (penalización = 0). |

## D. Software

| Término | Definición |
|---|---|
| **Ocean SDK** | Conjunto de librerías Python de D-Wave: `dimod`, `dwave-samplers`, `dwave-system`, `dwave-networkx`. Software libre. |
| **dimod.Binary** | Variable binaria simbólica: se suma, multiplica y eleva al cuadrado como en papel. |
| **SimulatedAnnealingSampler** | Recocido simulado rápido (`dwave-samplers`): `num_reads` runs de `num_sweeps` iteraciones. |
| **ExactSolver** | Fuerza bruta de dimod: prueba las 2ⁿ combinaciones. Solo para problemas pequeños. |
| **DADK** | *Digital Annealer Development Kit*: librería equivalente de Fujitsu para su Digital Annealer. |
| **dimod** | Librería de D-Wave para definir modelos (BQM, QUBO, Ising, CQM). |
| **BQM / CQM** | *Binary Quadratic Model* (QUBO/Ising) / *Constrained Quadratic Model* (permite restricciones explícitas, solvers híbridos). |
| **Sampler** | Objeto que resuelve un modelo: `ExactSolver` (fuerza bruta), `SimulatedAnnealingSampler`, `DWaveSampler` (QPU real), `LeapHybridSampler`… |
| **SampleSet** | Resultado de un sampler: soluciones, energías y número de apariciones. |
| **Jupyter Notebook (.ipynb)** | Cuaderno interactivo que mezcla código, texto, fórmulas y resultados. |
| **Qiskit / Cirq / Q#** | SDK de IBM, Google y Microsoft para ordenadores de puertas. |
