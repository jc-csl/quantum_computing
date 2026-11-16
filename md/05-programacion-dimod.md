# 5 · Programar QUBO en Python con D-Wave Ocean (dimod)

> **Objetivo de la unidad:** conocer las piezas básicas de la librería **dimod** (D-Wave Ocean) y resolver el ejemplo de los proyectos A/B con código Python. Escribiremos la fórmula **tal cual la hemos deducido en papel**: la librería se encarga del resto.

---

## 5.1 ¿Qué es Ocean / dimod?

**Ocean** es el conjunto de librerías Python de D-Wave. Es **software libre** y se instala con `pip`, sin necesidad de cuenta. Usaremos dos paquetes:

| Paquete | Qué aporta |
|---|---|
| `dimod` | Las **variables binarias** y el **modelo QUBO** (`BinaryQuadraticModel`), más un solver de fuerza bruta (`ExactSolver`) |
| `dwave-samplers` | El **recocido simulado** rápido (`SimulatedAnnealingSampler`), escrito en C++ |

El mismo modelo que resolvemos en el portátil se podría enviar, sin cambiar la formulación, a un ordenador cuántico de D-Wave a través de su nube (Leap) o, con la librería equivalente de Fujitsu, al Digital Annealer.

---

## 5.2 Las piezas de dimod

| Pieza | Para qué sirve |
|---|---|
| `dimod.Binary("A")` | Crea una **variable binaria** llamada `A` (vale 0 o 1) |
| `+  -  *  **2` | Las variables se combinan como en papel: sumas, productos y cuadrados |
| `H = objetivo + restriccion` | El resultado es un **BinaryQuadraticModel** (el QUBO). dimod expande y aplica x² = x solo |
| `H.linear` / `H.quadratic` / `H.offset` | Coeficientes lineales, cuadráticos y constante del QUBO |
| `H.num_variables` | Número de variables (bits) |
| `H.energy(sample)` | Energía de una combinación concreta |
| `dimod.ExactSolver().sample(H)` | **Fuerza bruta**: prueba todas las combinaciones (solo problemas pequeños) |
| `SimulatedAnnealingSampler().sample(H, num_reads, num_sweeps)` | **Recocido simulado**: `num_reads` runs de `num_sweeps` iteraciones |
| `resultado.first` | La mejor muestra: `.sample` (diccionario {variable: 0/1}) y `.energy` |
| `resultado.aggregate()` | Agrupa muestras iguales y cuenta `num_occurrences` (frecuencia) |

---

## 5.3 Pseudocódigo

```text
Definir los datos (beneficios, P)
Crear variables binarias x_A, x_B
objetivo     = −(3·x_A + 2·x_B)
restricción  = P · (x_A + x_B − 1)²
H            = objetivo + restricción
resultado    = SimulatedAnnealingSampler().sample(H, num_reads=10)
Leer la mejor muestra e interpretarla
Comprobar que la penalización vale 0
```

---

## 5.4 Código completo comentado

```python
# Ejercicio 1 — Selección del mejor beneficio con QUBO y dimod
import dimod
from dwave.samplers import SimulatedAnnealingSampler

# ── 1. DATOS ──────────────────────────────────────────────
beneficio_A = 3
beneficio_B = 2
P = 4                                 # P > max(beneficios) = 3

# ── 2. VARIABLES BINARIAS ─────────────────────────────────
x_A = dimod.Binary("A")               # 1 si elijo A
x_B = dimod.Binary("B")               # 1 si elijo B

# ── 3. OBJETIVO (maximizar → minimizar el negativo) ───────
objetivo = -beneficio_A * x_A - beneficio_B * x_B

# ── 4. PENALIZACIÓN: exactamente uno ──────────────────────
restriccion = P * (x_A + x_B - 1) ** 2   # dimod expande y aplica x² = x

# ── 5. HAMILTONIANO (el QUBO) ─────────────────────────────
H = objetivo + restriccion
print("Lineal:", dict(H.linear))       # {'A': -7.0, 'B': -6.0}
print("Cuadrático:", dict(H.quadratic))# {('B', 'A'): 8.0}
print("Constante:", H.offset)          # 4.0
print("Variables:", H.num_variables)   # 2

# ── 6a. FUERZA BRUTA (opcional, solo problemas pequeños) ──
print(dimod.ExactSolver().sample(H))   # las 4 combinaciones ordenadas por energía

# ── 6b. RECOCIDO SIMULADO ─────────────────────────────────
sampler = SimulatedAnnealingSampler()
resultado = sampler.sample(H, num_reads=10, num_sweeps=100)

# ── 7. INTERPRETAR ────────────────────────────────────────
mejor = resultado.first
cfg = mejor.sample                     # {'A': 1, 'B': 0}
print("A elegido:", bool(cfg["A"]), "| B elegido:", bool(cfg["B"]))
print("Beneficio:", beneficio_A * cfg["A"] + beneficio_B * cfg["B"])
print("Energía H:", mejor.energy)                    # -3.0
print("Penalización:", restriccion.energy(cfg))      # 0.0 → cumple
print("Veces encontrada:", resultado.aggregate().first.num_occurrences, "de 10")
```

Salida de `ExactSolver` (las 4 combinaciones, de mejor a peor):

```text
   A  B energy num_oc.
1  1  0   -3.0       1
2  0  1   -2.0       1
3  1  1   -1.0       1
0  0  0    4.0       1
```

---

## 5.5 Cómo busca el solver: los parámetros

El solver **no calcula** matemáticamente que 3 es mayor que 2. Convierte las opciones en un **paisaje de energía**: la mejor solución (elegir A, energía −3) es el **valle más profundo** y la segunda (elegir B, −2) un valle algo menos profundo.

| Combinación | 00 | 10 (A) | 01 (B) | 11 |
|---|:---:|:---:|:---:|:---:|
| Energía | 4 | **−3** | −2 | −1 |

Después lanza una **"canica"** que rueda por ese paisaje mientras la temperatura baja, como en el recocido de la unidad 3. Los parámetros controlan esa búsqueda:

| Parámetro | Qué es | En el ejemplo A/B |
|---|---|---|
| `num_reads` (**intentos**) | Cuántas veces se lanza la canica desde un punto **al azar**. Cada intento es independiente. | Con `num_reads=10`, los 10 intentos acaban en el valle de A: la solución A aparece **10 veces**. |
| `num_sweeps` (**barridos**) | Cuántos pasos da la canica en cada intento. En **un sweep** el algoritmo revisa **cada variable una vez**: "¿mejora si cambio A?", "¿y si cambio B?". | Con 2 variables solo hay 4 combinaciones: 100 sweeps sobran. Encuentra A en los primeros pasos y el resto confirma que no hay un valle mejor. |
| `beta_range` (**temperatura**) | β = 1/T. Al principio (T alta) la canica puede **subir** a soluciones peores para no quedarse atascada; al final (T baja) **solo baja** y se asienta en el valle. | Por defecto se calcula sola a partir de los coeficientes (3 y 2). La diferencia entre A y B es tan clara que llega a A enseguida. |
| `seed` (**semilla**) | El punto de salida y los saltos son aleatorios. Con una semilla fija los números "aleatorios" son siempre los mismos. | Con `seed=42` cada ejecución da **exactamente el mismo resultado**: útil para corregir prácticas. |

```python
resultado = SimulatedAnnealingSampler().sample(H, num_reads=10, num_sweeps=100, seed=42)
```

> Como el método es **probabilístico**, en problemas grandes no todos los intentos llegan a la misma solución. `resultado.aggregate()` agrupa las muestras iguales y `num_occurrences` dice cuántos intentos acabaron en cada una: es la **frecuencia** de la unidad 3.

---

## 5.6 Claves para comprobar un resultado

1. `restriccion.energy(cfg)` debe ser **0.0** → solución **factible**.
2. `mejor.energy` = −beneficio (o coste) cuando la penalización es 0.
3. Una **frecuencia alta** indica que el solver converge de forma estable.
4. Si salen soluciones inválidas: **subir P**, `num_sweeps` o `num_reads`.
5. En problemas pequeños (≤ 20 variables), `ExactSolver` da la respuesta exacta para comparar.

---

## 5.7 Del problema al código: resumen

```text
PROBLEMA REAL          QUBO                          dimod
───────────────        ─────────────────────         ───────────────────────────
"¿Elegir A o B?"   →   x_A, x_B ∈ {0,1}          →   dimod.Binary("A"), dimod.Binary("B")
"maximizar"        →   −(3x_A + 2x_B)            →   -3*x_A - 2*x_B
"solo uno"         →   P·(x_A + x_B − 1)²        →   P * (x_A + x_B - 1)**2
"resolver"         →   minimizar H               →   sampler.sample(H, num_reads=10)
"leer resultado"   →   bits de la solución       →   resultado.first.sample
```

### Y en el Digital Annealer de Fujitsu (DADK)
La librería de Fujitsu, **DADK**, sigue exactamente la misma idea con otros nombres: `Term(1, 0)` en vez de `dimod.Binary("A")`, `BinPol` en vez de `BinaryQuadraticModel`, `QUBOSolverCPU(number_runs, number_iterations)` en vez de `SimulatedAnnealingSampler().sample(H, num_reads, num_sweeps)` y `H.compute(cfg)` en vez de `H.energy(cfg)`. Lo importante es la **formulación QUBO**, que es la misma en ambos.

---

### Preguntas de repaso
1. ¿Qué devuelve `dimod.Binary("A")`?
2. ¿Para qué sirve `ExactSolver` y por qué no se usa en problemas grandes?
3. ¿Qué diferencia hay entre `num_reads` y `num_sweeps`? ¿Para qué sirve `seed`?
4. Si `restriccion.energy(cfg)` vale 4, ¿qué significa?

<details><summary>Soluciones</summary>

1. Una variable binaria (un modelo de una sola variable) que se puede sumar y multiplicar. 2. Prueba todas las combinaciones (2ⁿ): exacto pero inviable a partir de unas 20–25 variables. 3. `num_reads` = número de intentos independientes; `num_sweeps` = pasos (barridos) dentro de cada intento. `seed` fija los números aleatorios para repetir el mismo resultado. 4. La solución incumple una restricción: no es factible.
</details>
