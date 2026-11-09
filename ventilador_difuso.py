import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def construir_sistema():
    temperatura = ctrl.Antecedent(np.arange(0, 41, 0.5), "temperatura")
    humedad = ctrl.Antecedent(np.arange(0, 101, 1), "humedad")
    velocidad = ctrl.Consequent(np.arange(0, 101, 1), "velocidad")

    temperatura["fria"] = fuzz.trapmf(temperatura.universe, [0, 0, 10, 18])
    temperatura["templada"] = fuzz.trimf(temperatura.universe, [14, 22, 30])
    temperatura["caliente"] = fuzz.trapmf(temperatura.universe, [26, 33, 40, 40])

    humedad["baja"] = fuzz.trapmf(humedad.universe, [0, 0, 25, 45])
    humedad["media"] = fuzz.trimf(humedad.universe, [35, 55, 75])
    humedad["alta"] = fuzz.trapmf(humedad.universe, [65, 80, 100, 100])

    velocidad["apagado"] = fuzz.trimf(velocidad.universe, [0, 0, 20])
    velocidad["baja"] = fuzz.trimf(velocidad.universe, [10, 30, 50])
    velocidad["media"] = fuzz.trimf(velocidad.universe, [40, 60, 80])
    velocidad["alta"] = fuzz.trimf(velocidad.universe, [70, 100, 100])

    reglas = [
        ctrl.Rule(temperatura["fria"] & humedad["baja"], velocidad["apagado"]),
        ctrl.Rule(temperatura["fria"] & humedad["media"], velocidad["apagado"]),
        ctrl.Rule(temperatura["fria"] & humedad["alta"], velocidad["baja"]),
        ctrl.Rule(temperatura["templada"] & humedad["baja"], velocidad["baja"]),
        ctrl.Rule(temperatura["templada"] & humedad["media"], velocidad["media"]),
        ctrl.Rule(temperatura["templada"] & humedad["alta"], velocidad["media"]),
        ctrl.Rule(temperatura["caliente"] & humedad["baja"], velocidad["media"]),
        ctrl.Rule(temperatura["caliente"] & humedad["media"], velocidad["alta"]),
        ctrl.Rule(temperatura["caliente"] & humedad["alta"], velocidad["alta"]),
    ]

    sistema = ctrl.ControlSystem(reglas)
    return sistema, temperatura, humedad, velocidad


def evaluar(sistema, temp, hum):
    simulacion = ctrl.ControlSystemSimulation(sistema)
    simulacion.input["temperatura"] = temp
    simulacion.input["humedad"] = hum
    simulacion.compute()
    return simulacion.output["velocidad"], simulacion


def main():
    sistema, _, _, _ = construir_sistema()
    casos = [
        (5, 30),
        (10, 85),
        (22, 20),
        (22, 55),
        (24, 80),
        (30, 20),
        (35, 55),
        (38, 90),
    ]
    print(f"{'Temperatura (C)':>16} {'Humedad (%)':>12} {'Velocidad (%)':>14}")
    print("-" * 44)
    for temp, hum in casos:
        salida, _ = evaluar(sistema, temp, hum)
        print(f"{temp:>16} {hum:>12} {salida:>14.2f}")


if __name__ == "__main__":
    main()
