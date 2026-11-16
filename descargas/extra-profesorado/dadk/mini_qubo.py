"""
mini_qubo.py — Simulador QUBO didáctico (Python puro, sin dependencias)
=======================================================================

Imita la parte de la API de Fujitsu DADK que se usa en los ejercicios de clase
(BinPol, Term, QUBOSolverCPU) para poder practicar SIN tener instalado DADK.

Uso: en los ejercicios, cambia

    from dadk.BinPol import BinPol, Term
    from dadk.QUBOSolverCPU import QUBOSolverCPU

por

    from mini_qubo import BinPol, Term, QUBOSolverCPU

y el resto del código funciona igual.

Diferencias con DADK (a propósito, para que sea fácil de entender):
  * El solver es un recocido simulado (simulated annealing) clásico de un bit
    por paso, con temperatura que baja de forma geométrica. No es el algoritmo
    del Digital Annealer, pero sigue la misma idea.
  * ``solution.energy`` devuelve la energía REAL (en DADK sale escalada a enteros
    grandes; allí hay que usar ``H.compute(config)``). ``H.compute`` funciona en ambos.
  * Incluye ``exact_minimize(H)``: prueba TODAS las combinaciones (fuerza bruta)
    para comprobar resultados en problemas pequeños (hasta ~22 bits).

Material didáctico — Cloud, IoT and Quantum Computing (ASIR).
"""
from __future__ import annotations

import itertools
import math
import random
import time
from datetime import timedelta

__all__ = ["BinPol", "Term", "QUBOSolverCPU", "exact_minimize"]


# ─────────────────────────────────────────────────────────────────────────────
#  POLINOMIOS BINARIOS
# ─────────────────────────────────────────────────────────────────────────────
def _num(v):
    """Muestra 4.0 como 4 y deja los decimales cuando hacen falta."""
    return int(v) if float(v).is_integer() else v


class BinPol:
    """Polinomio en variables binarias x_i ∈ {0,1}.

    Internamente es un diccionario {monomio: coeficiente}, donde el monomio es
    una tupla ordenada de índices de bit:  ()  → constante,  (0,) → x_0,
    (0, 1) → x_0·x_1.  Como x² = x en binario, los índices nunca se repiten.
    """

    def __init__(self, terms=None):
        self.terms: dict[tuple, float] = {}
        if terms:
            for mono, coef in terms.items():
                self._add(tuple(sorted(set(mono))), coef)

    # ── utilidades internas ──────────────────────────────────────────────────
    def _add(self, mono, coef):
        if coef == 0:
            return
        v = self.terms.get(mono, 0) + coef
        if v == 0:
            self.terms.pop(mono, None)
        else:
            self.terms[mono] = v

    @staticmethod
    def _as_pol(other):
        if isinstance(other, BinPol):
            return other
        if isinstance(other, (int, float)):
            return BinPol({(): other})
        return NotImplemented

    def copy(self):
        return BinPol(dict(self.terms))

    # ── aritmética ───────────────────────────────────────────────────────────
    def __add__(self, other):
        other = self._as_pol(other)
        if other is NotImplemented:
            return other
        r = self.copy()
        for m, c in other.terms.items():
            r._add(m, c)
        return r

    __radd__ = __add__

    def __neg__(self):
        return BinPol({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        other = self._as_pol(other)
        if other is NotImplemented:
            return other
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        other = self._as_pol(other)
        if other is NotImplemented:
            return other
        r = BinPol()
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                # x_i · x_i = x_i  →  unión de índices sin repetir
                r._add(tuple(sorted(set(m1) | set(m2))), c1 * c2)
        return r

    __rmul__ = __mul__

    def __pow__(self, k):
        if not isinstance(k, int) or k < 0:
            raise ValueError("Solo se admiten potencias enteras >= 0")
        r = BinPol({(): 1})
        for _ in range(k):
            r = r * self
        return r

    @staticmethod
    def sum(iterable):
        """Suma una secuencia de BinPol/Term (equivalente a BinPol.sum de DADK)."""
        r = BinPol()
        for p in iterable:
            r = r + p
        return r

    # ── consulta ─────────────────────────────────────────────────────────────
    @property
    def N(self):
        """Número de bits del problema (índice máximo + 1)."""
        idx = [i for m in self.terms for i in m]
        return max(idx) + 1 if idx else 0

    @property
    def degree(self):
        return max((len(m) for m in self.terms), default=0)

    def compute(self, config):
        """Evalúa el polinomio para una configuración (dict {bit: 0/1} o lista)."""
        total = 0
        for m, c in self.terms.items():
            if all(config[i] for i in m):
                total += c
        return float(total)

    def as_qubo(self):
        """Devuelve (lineal, cuadrático, constante) -> útil para dimod.from_qubo."""
        lin, quad, const = {}, {}, 0
        for m, c in self.terms.items():
            if len(m) == 0:
                const += c
            elif len(m) == 1:
                lin[m[0]] = lin.get(m[0], 0) + c
            elif len(m) == 2:
                quad[m] = quad.get(m, 0) + c
            else:
                raise ValueError("El polinomio tiene grado > 2: no es un QUBO")
        return lin, quad, const

    def matrix(self):
        """Matriz Q triangular superior (lista de listas). Diagonal = lineales."""
        n = self.N
        Q = [[0] * n for _ in range(n)]
        lin, quad, _ = self.as_qubo()
        for i, c in lin.items():
            Q[i][i] = _num(c)
        for (i, j), c in quad.items():
            Q[i][j] = _num(c)
        return Q

    def __str__(self):
        if not self.terms:
            return "0"
        parts = []
        for k, (m, c) in enumerate(sorted(self.terms.items())):
            v = _num(abs(c))
            vars_ = " ".join(f"bit_{i}" for i in m)
            body = f"{v} {vars_}".strip() if (v != 1 or not m) else vars_
            sign = "-" if c < 0 else "+"
            if k == 0:
                parts.append(("- " if c < 0 else "") + body)
            else:
                parts.append(f"{sign} {body}")
        return " ".join(parts)

    __repr__ = __str__


def Term(coef, index):
    """Monomio coef · x_index (igual que dadk.BinPol.Term)."""
    return BinPol({(index,): coef})


# ─────────────────────────────────────────────────────────────────────────────
#  RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────
class Solution:
    def __init__(self, configuration, energy, frequency):
        self.configuration = configuration   # dict {bit: 0/1}
        self.energy = energy                  # energía real
        self.frequency = frequency            # nº de runs que acabaron aquí

    def bits(self):
        return "".join(str(self.configuration[i]) for i in sorted(self.configuration))

    def __repr__(self):
        return f"Solution(bits={self.bits()}, energy={_num(self.energy)}, frequency={self.frequency})"


class _Times:
    def __init__(self, seconds):
        self.duration_execution = timedelta(seconds=seconds)


class _Graphics:
    def __init__(self):
        self.temperature, self.energy, self.best = [], [], []

    def plot_graphs(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
        ax[0].plot(self.temperature, color="#d9534f")
        ax[0].set_title("Temperatura T (run 1)")
        ax[0].set_xlabel("iteración")
        ax[1].plot(self.energy, color="#999", lw=0.8, label="energía actual")
        ax[1].plot(self.best, color="#1f6feb", lw=2, label="mejor energía")
        ax[1].set_title("Energía H (run 1)")
        ax[1].set_xlabel("iteración")
        ax[1].legend()
        plt.tight_layout()
        plt.show()


class SolutionList:
    def __init__(self, solutions, seconds, graphics=None):
        self.solutions = solutions
        self.min_solution = solutions[0]
        self.solver_times = _Times(seconds)
        self.graphics_data = graphics

    def __repr__(self):
        return "\n".join(map(repr, self.solutions))


# ─────────────────────────────────────────────────────────────────────────────
#  SOLVER: RECOCIDO SIMULADO
# ─────────────────────────────────────────────────────────────────────────────
class QUBOSolverCPU:
    """Recocido simulado de un bit por iteración.

    Parámetros (mismos nombres que DADK; los que no se usan se ignoran):
      number_runs        nº de ejecuciones independientes (cada una parte al azar)
      number_iterations  nº de pasos por ejecución
      temperature_start  temperatura inicial (si None se calcula sola)
      temperature_end    temperatura final   (si None se calcula sola)
      random_seed        semilla para repetir resultados
      graphics           guarda la evolución de T y H del primer run
    """

    def __init__(self, number_runs=16, number_iterations=1000,
                 temperature_start=None, temperature_end=None,
                 random_seed=None, graphics=False, **kwargs):
        self.number_runs = int(number_runs)
        self.number_iterations = int(number_iterations)
        self.temperature_start = temperature_start
        self.temperature_end = temperature_end
        self.rng = random.Random(random_seed)
        self.graphics = graphics

    def minimize(self, H: BinPol) -> SolutionList:
        t0 = time.perf_counter()
        n = H.N
        lin, quad, const = H.as_qubo()
        h = [0.0] * n
        nb = [[] for _ in range(n)]          # vecinos: (j, J_ij)
        for i, c in lin.items():
            h[i] += c
        for (i, j), c in quad.items():
            nb[i].append((j, c))
            nb[j].append((i, c))

        # Temperaturas automáticas a partir del mayor cambio de energía posible
        max_d = max((abs(h[i]) + sum(abs(c) for _, c in nb[i]) for i in range(n)), default=1) or 1
        min_d = min((abs(c) for c in list(lin.values()) + list(quad.values()) if c), default=1)
        T0 = self.temperature_start or max_d / math.log(2)     # al inicio acepta mucho
        T1 = self.temperature_end or max(min_d / math.log(100), 1e-6)  # al final casi nada
        steps = max(self.number_iterations, 1)
        alpha = (T1 / T0) ** (1 / max(steps - 1, 1))

        found = {}
        gdata = _Graphics() if self.graphics else None
        for run in range(self.number_runs):
            x = [self.rng.randint(0, 1) for _ in range(n)]
            E = H.compute(x)
            best_x, best_E = x[:], E
            T = T0
            for it in range(steps):
                i = self.rng.randrange(n)
                # ΔE al cambiar el bit i:  (1-2x_i)·(h_i + Σ J_ij x_j)
                field = h[i] + sum(c * x[j] for j, c in nb[i])
                dE = (1 - 2 * x[i]) * field
                if dE <= 0 or self.rng.random() < math.exp(-dE / T):
                    x[i] = 1 - x[i]
                    E += dE
                    if E < best_E - 1e-12:
                        best_x, best_E = x[:], E
                if gdata is not None and run == 0:
                    gdata.temperature.append(T)
                    gdata.energy.append(E)
                    gdata.best.append(best_E)
                T *= alpha
            key = tuple(best_x)
            found[key] = found.get(key, 0) + 1

        sols = [Solution({i: b for i, b in enumerate(k)}, H.compute(k), f)
                for k, f in found.items()]
        sols.sort(key=lambda s: (s.energy, -s.frequency))
        return SolutionList(sols, time.perf_counter() - t0, gdata)


def exact_minimize(H: BinPol, top=10):
    """Fuerza bruta: evalúa las 2^N configuraciones. Devuelve las 'top' mejores."""
    n = H.N
    if n > 22:
        raise ValueError(f"{n} bits = {2**n} combinaciones: demasiadas para fuerza bruta")
    res = []
    for bits in itertools.product((0, 1), repeat=n):
        res.append(Solution({i: b for i, b in enumerate(bits)}, H.compute(bits), 1))
    res.sort(key=lambda s: s.energy)
    return res[:top]


if __name__ == "__main__":
    # Prueba rápida: ejercicio 1 (elegir A o B)
    xA, xB = Term(1, 0), Term(1, 1)
    H = -3 * xA - 2 * xB + 4 * (xA + xB - 1) ** 2
    print("H =", H)
    print("Matriz Q:", H.matrix())
    sl = QUBOSolverCPU(number_runs=8, number_iterations=200, random_seed=1).minimize(H)
    print(sl)
    print("Fuerza bruta:", exact_minimize(H, top=4))
