"""Demo grafica con controles deslizantes.

Mueve los sliders de temperatura y humedad: las graficas muestran en vivo
los grados de pertenencia, las reglas activadas, el conjunto agregado
(area sombreada) y el centroide (linea negra) con la velocidad final.

Uso:  python demo_sliders.py
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from ventilador_difuso import construir_sistema, evaluar
from demo import grados, reglas_activadas, agregacion

TEMP_INICIAL = 24
HUM_INICIAL = 80


def dibujar_terminos(eje, variable):
    for nombre, termino in variable.terms.items():
        eje.plot(variable.universe, termino.mf, label=nombre, linewidth=1.5)
    eje.set_ylim(0, 1.05)
    eje.set_ylabel("Grado de pertenencia")
    eje.legend(loc="upper right", fontsize=8)


def main():
    sistema, temperatura, humedad, velocidad = construir_sistema()

    fig = plt.figure(figsize=(12, 8))
    fig.canvas.manager.set_window_title("Controlador difuso del ventilador")
    rejilla = fig.add_gridspec(2, 2, height_ratios=[1, 1.2], left=0.07,
                               right=0.97, top=0.93, bottom=0.26,
                               hspace=0.45, wspace=0.2)
    ax_t = fig.add_subplot(rejilla[0, 0])
    ax_h = fig.add_subplot(rejilla[0, 1])
    ax_v = fig.add_subplot(rejilla[1, :])

    dibujar_terminos(ax_t, temperatura)
    dibujar_terminos(ax_h, humedad)
    dibujar_terminos(ax_v, velocidad)
    ax_t.set_xlabel("Temperatura (C)")
    ax_h.set_xlabel("Humedad (%)")
    ax_v.set_xlabel("Velocidad (%)")

    linea_t = ax_t.axvline(TEMP_INICIAL, color="black", linestyle="--")
    linea_h = ax_h.axvline(HUM_INICIAL, color="black", linestyle="--")
    linea_v = ax_v.axvline(0, color="black", linewidth=3)
    relleno = [ax_v.fill_between(velocidad.universe, 0, 0)]

    texto_reglas = fig.text(0.07, 0.035, "", family="monospace", fontsize=9,
                            va="bottom")

    ax_s_t = fig.add_axes([0.12, 0.14, 0.33, 0.03])
    ax_s_h = fig.add_axes([0.6, 0.14, 0.33, 0.03])
    s_temp = Slider(ax_s_t, "Temperatura", 0, 40, valinit=TEMP_INICIAL,
                    valstep=0.5, valfmt="%.1f C")
    s_hum = Slider(ax_s_h, "Humedad", 0, 100, valinit=HUM_INICIAL,
                   valstep=1, valfmt="%.0f %%")

    def actualizar(_=None):
        temp, hum = s_temp.val, s_hum.val
        g_temp = grados(temperatura, temp)
        g_hum = grados(humedad, hum)
        activas = reglas_activadas(sistema, g_temp, g_hum)
        salida, _ = evaluar(sistema, temp, hum)

        linea_t.set_xdata([temp, temp])
        linea_h.set_xdata([hum, hum])
        ax_t.set_title("  ".join(f"{n}={v:.2f}" for n, v in g_temp.items()),
                       fontsize=10)
        ax_h.set_title("  ".join(f"{n}={v:.2f}" for n, v in g_hum.items()),
                       fontsize=10)

        relleno[0].remove()
        relleno[0] = ax_v.fill_between(velocidad.universe, 0,
                                       agregacion(velocidad, activas),
                                       color="tab:green", alpha=0.35)
        linea_v.set_xdata([salida, salida])
        ax_v.set_title(f"T = {temp:.1f} C, H = {hum:.0f} %  ->  "
                       f"velocidad = {salida:.1f} %",
                       fontsize=13, fontweight="bold")

        lineas = [f"{t} Y {h} -> {s} (fuerza {f:.2f})"
                  for t, h, s, f in activas]
        texto_reglas.set_text("Reglas activadas:\n" + "\n".join(lineas))
        fig.canvas.draw_idle()

    s_temp.on_changed(actualizar)
    s_hum.on_changed(actualizar)
    actualizar()
    plt.show()
    return fig, s_temp, s_hum


if __name__ == "__main__":
    main()
