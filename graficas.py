import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ventilador_difuso import construir_sistema, evaluar

CARPETA = "figuras"


def guardar(fig, nombre):
    ruta = os.path.join(CARPETA, nombre)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Guardada:", ruta)


def funciones_pertenencia(temperatura, humedad, velocidad):
    for variable, nombre in [
        (temperatura, "membresia_temperatura.png"),
        (humedad, "membresia_humedad.png"),
        (velocidad, "membresia_velocidad.png"),
    ]:
        variable.view()
        fig = plt.gcf()
        fig.set_size_inches(7, 3.5)
        for eje in fig.axes:
            eje.set_ylabel("Grado de pertenencia")
        plt.title(variable.label)
        guardar(fig, nombre)


def agregacion_defuzzificacion(sistema, velocidad, temp, hum, nombre):
    salida, sim = evaluar(sistema, temp, hum)
    velocidad.view(sim=sim)
    fig = plt.gcf()
    fig.set_size_inches(7, 3.5)
    for eje in fig.axes:
        eje.set_ylabel("Grado de pertenencia")
    plt.title(f"T={temp} C, H={hum}% -> velocidad = {salida:.2f}%")
    guardar(fig, nombre)


def superficie(sistema):
    temps = np.linspace(0, 40, 41)
    hums = np.linspace(0, 100, 41)
    X, Y = np.meshgrid(temps, hums)
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j], _ = evaluar(sistema, X[i, j], Y[i, j])

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none")
    ax.set_xlabel("Temperatura (C)")
    ax.set_ylabel("Humedad (%)")
    ax.set_zlabel("Velocidad (%)")
    ax.set_title("Superficie de control")
    ax.view_init(30, 225)
    fig.colorbar(surf, shrink=0.6)
    guardar(fig, "superficie_control.png")


def main():
    os.makedirs(CARPETA, exist_ok=True)
    sistema, temperatura, humedad, velocidad = construir_sistema()
    funciones_pertenencia(temperatura, humedad, velocidad)
    agregacion_defuzzificacion(sistema, velocidad, 24, 80, "defuzzificacion_24_80.png")
    agregacion_defuzzificacion(sistema, velocidad, 35, 55, "defuzzificacion_35_55.png")
    superficie(sistema)


if __name__ == "__main__":
    main()
