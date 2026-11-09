"""Demo interactiva en consola del controlador difuso del ventilador.

Pide una temperatura y una humedad, y muestra cada paso de la inferencia:
fuzzificacion, reglas activadas y velocidad final (centroide).

Uso:  python demo.py
"""

import numpy as np
import skfuzzy as fuzz

from ventilador_difuso import construir_sistema, evaluar

RANGO_TEMP = (0, 40)
RANGO_HUM = (0, 100)


def limitar(valor, rango):
    """Recorta el valor al rango valido de la variable."""
    return min(max(valor, rango[0]), rango[1])


def grados(variable, valor):
    """Grado de pertenencia del valor en cada termino de la variable."""
    return {
        nombre: float(fuzz.interp_membership(variable.universe, termino.mf, valor))
        for nombre, termino in variable.terms.items()
    }


def reglas_activadas(sistema, g_temp, g_hum):
    """Lista (temp, hum, velocidad, fuerza) de las reglas con fuerza > 0.

    La fuerza de cada regla es el minimo de sus dos antecedentes (operador Y).
    """
    activas = []
    for regla in sistema.rules:
        t, h = regla.antecedent_terms
        salida = regla.consequent[0].term.label
        fuerza = min(g_temp[t.label], g_hum[h.label])
        if fuerza > 0:
            activas.append((t.label, h.label, salida, fuerza))
    return activas


def agregacion(velocidad, activas):
    """Conjunto agregado de la salida: cada termino recortado a su fuerza
    maxima y unido con el maximo (inferencia de Mamdani)."""
    agregado = np.zeros_like(velocidad.universe, dtype=float)
    for nombre, termino in velocidad.terms.items():
        fuerza = max((f for _, _, s, f in activas if s == nombre), default=0)
        agregado = np.fmax(agregado, np.fmin(fuerza, termino.mf))
    return agregado


def leer_numero(mensaje):
    """Lee un numero; devuelve None si el usuario escribe 'salir'."""
    while True:
        texto = input(mensaje).strip().lstrip("﻿").lower()
        if texto in ("salir", "s", "q"):
            return None
        try:
            return float(texto.replace(",", "."))
        except ValueError:
            print("  Escribe un numero (o 'salir' para terminar).")


def formatear(g):
    return " | ".join(f"{nombre}: {valor:.2f}" for nombre, valor in g.items())


def main():
    sistema, temperatura, humedad, _ = construir_sistema()
    print("=" * 56)
    print(" Controlador difuso del ventilador - demo interactiva")
    print(" Escribe 'salir' en cualquier momento para terminar.")
    print("=" * 56)

    while True:
        print()
        temp = leer_numero("Temperatura (C, 0-40): ")
        if temp is None:
            break
        hum = leer_numero("Humedad (%, 0-100):    ")
        if hum is None:
            break

        t_ok, h_ok = limitar(temp, RANGO_TEMP), limitar(hum, RANGO_HUM)
        if t_ok != temp:
            print(f"  Aviso: temperatura fuera de rango, se usa {t_ok:g} C.")
        if h_ok != hum:
            print(f"  Aviso: humedad fuera de rango, se usa {h_ok:g} %.")

        g_temp = grados(temperatura, t_ok)
        g_hum = grados(humedad, h_ok)

        print("\n1) Fuzzificacion")
        print(f"   Temperatura -> {formatear(g_temp)}")
        print(f"   Humedad     -> {formatear(g_hum)}")

        print("\n2) Reglas activadas (fuerza = minimo de los dos grados)")
        for t, h, s, f in reglas_activadas(sistema, g_temp, g_hum):
            print(f"   {t} Y {h} -> {s:<8} (fuerza {f:.2f})")

        salida, _ = evaluar(sistema, t_ok, h_ok)
        print("\n3) Agregacion y defuzzificacion por centroide")
        print(f"   Velocidad del ventilador: {salida:.1f} %")

    print("\nFin de la demo.")


if __name__ == "__main__":
    main()
