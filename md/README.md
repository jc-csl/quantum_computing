# Introducción a la Computación Cuántica · Quantum Annealing y modelo QUBO

**Módulo:** Cloud, IoT and Quantum Computing · **Ciclo:** CFGS Administración de Sistemas Informáticos en Red (ASIR)

*Proyecto "ANNEALING: Computación Cuántica para problemas de Optimización" — Viceconsejería de Formación Profesional de Euskadi (curso 2025-26). Autores: Jaime Corrales y Juan Carlos San Román.*

![Semáforo IA verde](../img/ia-verde.png)

> **Declaración de uso de IA** (Guía de uso de la IA en el aula · Centro San Luis · nivel verde): este material parte de los apuntes propios del profesorado. Se ha utilizado IA para la mejora de redacción, el formateo, la generación de gráficos explicativos y los simuladores, con revisión y validación del profesorado.

## Índice

| # | Unidad | Contenido |
|---|---|---|
| 1 | [Conceptos básicos de computación cuántica](01-fundamentos-computacion-cuantica.md) | Qubit, esfera de Bloch, superposición, medición, interferencia, entrelazamiento, decoherencia, efecto túnel |
| 2 | [Hardware cuántico y estado actual](02-hardware-y-estado-actual.md) | Tipos de qubits, puertas vs annealing, fabricantes, NISQ, modo híbrido, criptografía, SDK |
| 3 | [Quantum Annealing](03-quantum-annealing.md) | Paisaje de energía, clásico vs cuántico, temperatura, iteraciones y runs, D-Wave vs Fujitsu |
| 4 | [El modelo QUBO](04-modelo-qubo.md) | Vocabulario, receta de formulación, ejemplo paso a paso, matriz Q, penalizaciones |
| 5 | [Programar con D-Wave Ocean (dimod)](05-programacion-dimod.md) | dimod.Binary, BinaryQuadraticModel, SimulatedAnnealingSampler, ExactSolver, parámetros |
| 6 | [Glosario](06-glosario.md) | Términos clave |
| 7 | [Prácticas](07-practicas.md) | Entorno (tabla de comandos Windows/Linux), simulador web, método de 7 pasos, 5 ejercicios guiados + 1 de ampliación con código comentado |

## Material descargable (`descargas/`)

| Fichero | Descripción |
|---|---|
| `prueba_entorno.py` | Comprobación del entorno (Práctica 0) |
| `ejercicio1_beneficio.py` | Elegir el proyecto con más beneficio (2 variables) |
| `ejercicio2_servidores.py` | Dejar encendidos 2 de 4 servidores (4 variables) |
| `ejercicio3_tareas.py` | Repartir tareas entre dos técnicos (6 variables) |
| `ejercicio4_particion.py` | Equilibrar VMs entre dos hosts (4 variables) |
| `ejercicio5_maxcut.py` | Max-Cut de una red de 7 equipos (7 variables) |
| `ejercicio6_maxcut_n_nodos.py` | Ampliación: Max-Cut de N nodos |
| `extra-profesorado/` | **Solo profesorado**: ejercicios avanzados (mochila con holgura, TSP), script Max-Cut original y versión Fujitsu DADK de los ejercicios |

## Guía rápida para el profesorado

| Sesión | Contenido | Material |
|---|---|---|
| 1 | Unidad 1: conceptos cuánticos (simuladores de qubit, 2ⁿ e interferencia) | Web, modo presentación |
| 2 | Unidad 2: hardware y estado actual | Web |
| 3 | Unidad 3: annealing (simulador de recocido) | Web |
| 4 | Unidad 4: modelo QUBO, ejemplo A/B a mano y en el simulador web | Web, laboratorio QUBO |
| 5 | Unidad 5 + Práctica 0: instalar entorno y ejecutar `prueba_entorno.py` | Tabla de comandos |
| 6 | Ejercicios 1–2 (proyecto, servidores) | `descargas/` |
| 7 | Ejercicios 3–4 (tareas, VMs) | `descargas/` |
| 8 | Ejercicio 5 (Max-Cut), ampliación 6 y entrega | `descargas/` |

Decisión de diseño: se usa **un único simulador**, el `SimulatedAnnealingSampler` de D-Wave Ocean, y el modelo se escribe siempre de forma **simbólica** (`dimod.Binary`, sumas, productos y cuadrados), sin construir matrices a mano. La matriz Q se explica en la unidad 4 solo como forma de leer el modelo.

## Correcciones respecto a los documentos originales
- Ejemplo A/B (unidad 4): el texto decía "escoger el proyecto **B** que tiene beneficio 3"; es el **A**. La matriz Q correcta es **Q₁₁ = −7, Q₂₂ = −6, Q₁₂ = 8** (constante +4), coherente con H = 8x₁x₂ − 7x₁ − 6x₂ + 4.
- Notebook original, ejercicio de la mochila (ahora en `extra-profesorado`): el óptimo es **Switch + Punto de acceso + Cableado = 15**, no Router + Switch = 14.
- Notebook original, ejercicio TSP (ahora en `extra-profesorado`): la distancia óptima es **14** (A→B→C→D→A), no 18.
- Glosario: el D-Wave Advantage tiene **5.000+** qubits y el Advantage2 **4.400+** (no 2.048, que correspondía al antiguo D-Wave 2000Q).
- Notebook DADK (anexo): `QUBOSolverCPU` emula en CPU el recocido del Digital Annealer (no "Simulated Bifurcation", que es la técnica de otro fabricante).

## Bibliografía y enlaces
- IBM — [¿Qué es la computación cuántica?](https://www.ibm.com/es-es/think/topics/quantum-computing)
- D-Wave — [Introducción al Quantum Annealing](https://docs.dwavequantum.com/en/latest/quantum_research/quantum_annealing_intro.html)
- Fujitsu — [Digital Annealer](https://global.fujitsu/en-us/local/technology/research/areas/digital-annealer)
- D-Wave — [dwave-samplers (simulated annealing libre)](https://github.com/dwavesystems/dwave-samplers)
- Patrick, Alan H. *Quantum for Everyone* (2025).
- Vídeo: [Física cuántica, los conceptos básicos en 25 minutos](https://youtu.be/bkUjjTwluQI)
- Simuladores: [Grok the Bloch Sphere](https://javafxpert.github.io/grok-bloch/) · [Entanglement qubits](https://entanglementqbits.netlify.app/)

---

> **Declaración de uso de IA** (Guía de uso de la IA en el aula · Centro San Luis · nivel verde): este material parte de los apuntes propios del profesorado. Se ha utilizado IA para la mejora de redacción, el formateo, la generación de gráficos explicativos y los simuladores, con revisión y validación del profesorado.
