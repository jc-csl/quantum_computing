# Quantum Annealing y modelo QUBO

**Apuntes, simuladores y prácticas de introducción a la computación cuántica**
Módulo *Cloud, IoT and Quantum Computing* · CFGS Administración de Sistemas Informáticos en Red (ASIR) · **Centro San Luis**

Con la colaboración de CIFP Txurdinaga LHII y Tknika · Proyecto ANNEALING, Viceconsejería de Formación Profesional de Euskadi (curso 2025-26) · Autores: Jaime Corrales y Juan Carlos San Román

> 🌐 **Web de apuntes:** `https://jc-csl.github.io/quantum_computing/` 
---

## Qué contiene

Una web de apuntes que se usa en el aula de dos formas:

- **Como documento**: índice lateral y diapositivas una debajo de otra.
- **En modo presentación**: una diapositiva a pantalla completa. Se entra con la tecla `P`, se avanza con `←` `→` y se sale con `Esc` (`F` = pantalla completa).

| # | Unidad | Contenido |
|---|---|---|
| 1 | Conceptos básicos | Qubit, esfera de Bloch, superposición, medición, interferencia, entrelazamiento, decoherencia, efecto túnel |
| 2 | Hardware y estado actual | Tipos de qubits, puertas lógicas vs annealing, fabricantes, era NISQ, modo híbrido, criptografía, SDK |
| 3 | Quantum Annealing | Paisaje de energía, recocido clásico vs cuántico, temperatura, iteraciones e intentos, D-Wave vs Fujitsu |
| 4 | Modelo QUBO | Objetivo + penalizaciones, ejemplo resuelto paso a paso, matriz Q, elección de la penalización P |
| 5 | Programar con dimod | `dimod.Binary`, `SimulatedAnnealingSampler`, `ExactSolver`, parámetros del solver |
| 6 | Glosario | ~50 términos con buscador |
| 7 | Prácticas | Entorno, tabla de comandos Windows/Linux, método de 7 pasos, 5 ejercicios guiados + 1 de ampliación |

**Simuladores interactivos en la web** (no necesitan instalar nada): medición de un qubit, bits frente a qubits (2ⁿ), interferencia de ondas, recocido sobre un paisaje de energía y un laboratorio QUBO con los ejercicios precargados.

## Estructura del repositorio

```text
├── index.html          Web de apuntes (página de GitHub Pages)
├── img/                Imágenes y gráficos de los apuntes
├── web/                Copia .txt de los scripts, para verlos desde la web
├── md/                 Los mismos apuntes en Markdown, por unidades
│   ├── README.md       Índice, guía docente por sesiones y correcciones
│   └── 01-…  07-….md
├── descargas/          Scripts Python de las prácticas
│   ├── prueba_entorno.py
│   ├── ejercicio1_beneficio.py       (2 variables)
│   ├── ejercicio2_servidores.py      (4 variables)
│   ├── ejercicio3_tareas.py          (6 variables)
│   ├── ejercicio4_particion.py       (4 variables)
│   ├── ejercicio5_maxcut.py          (7 variables)
│   ├── ejercicio6_maxcut_n_nodos.py  (ampliación)
│   └── extra-profesorado/            Ejercicios avanzados y versión Fujitsu DADK
├── .nojekyll           Indica a GitHub Pages que sirva los ficheros tal cual
└── .gitignore
```

## Prácticas: puesta en marcha rápida

Un único entorno para todo el módulo: **Python 3.11 o 3.12 + D-Wave Ocean** (`dimod` y `dwave-samplers`). Es software libre y no necesita cuenta.

| Acción | Windows (PowerShell) | Linux / macOS (bash) |
|---|---|---|
| Crear entorno virtual | `python -m venv qubo` | `python3 -m venv qubo` |
| Activar entorno | `.\qubo\Scripts\Activate.ps1` | `source qubo/bin/activate` |
| Instalar librerías | `pip install dimod dwave-samplers matplotlib networkx` | igual |
| Comprobar el entorno | `python descargas/prueba_entorno.py` | igual |
| Ejecutar un ejercicio | `python descargas/ejercicio1_beneficio.py` | igual |

Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Salida esperada de la prueba:

```text
H lineal: {'A': -7.0, 'B': -6.0} | cuadrático: {('B', 'A'): 8.0} | offset: 4.0
Mejor: {'A': 1, 'B': 0} Energía: -3.0
```

Todos los ejercicios siguen la misma plantilla de 7 pasos (datos → variables → objetivo → restricción → H → resolver → interpretar), con comentarios en cada bloque.

---

## Licencia

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es) (reconocimiento, no comercial, compartir igual). Añade el fichero `LICENSE` correspondiente al repositorio.

## Declaración de uso de IA

*Guía de uso de la IA en el aula · Centro San Luis · nivel verde.* Este material parte de los apuntes propios del profesorado. Se ha utilizado inteligencia artificial para la mejora de redacción, el formateo, la generación de gráficos explicativos y los simuladores, con revisión y validación del profesorado.
