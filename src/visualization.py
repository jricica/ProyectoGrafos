"""
Módulo de visualización del grafo de pases con NetworkX + Matplotlib.
Requisito 3.3: presentar el grafo de forma clara para la exposición.

El grafo se dibuja sobre una cancha (120x80, estándar StatsBomb), ubicando
a cada jugador cerca de su posición promedio real (pass network)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from src.cleaning import NOMBRES_CORTOS, calcular_posiciones

def _renombrar_corto(G):
    """Devuelve una copia del grafo con nombres cortos (o el original si no está en el diccionario)."""
    mapeo = {nodo: NOMBRES_CORTOS.get(nodo, nodo) for nodo in G.nodes()}
    return nx.relabel_nodes(G, mapeo)


def _dibujar_cancha(ax):
    """Dibuja las líneas de una cancha de fútbol (120x80) como fondo del grafo."""
    verde = '#2E7D32'
    linea = 'white'

    ax.set_facecolor(verde)
    ax.add_patch(patches.Rectangle((0, 0), 120, 80, fill=False, edgecolor=linea, linewidth=2))
    ax.plot([60, 60], [0, 80], color=linea, linewidth=1.5)
    ax.add_patch(patches.Circle((60, 40), 9.15, fill=False, edgecolor=linea, linewidth=1.5))
    ax.plot(60, 40, marker='o', color=linea, markersize=2)

    for x_area, direccion in [(0, 1), (120, -1)]:
        ax.add_patch(patches.Rectangle(
            (x_area if direccion == 1 else x_area - 18, 18), 18, 44,
            fill=False, edgecolor=linea, linewidth=1.5
        ))
        ax.add_patch(patches.Rectangle(
            (x_area if direccion == 1 else x_area - 6, 30), 6, 20,
            fill=False, edgecolor=linea, linewidth=1.5
        ))

    ax.set_xlim(-3, 123)
    ax.set_ylim(-3, 83)
    ax.set_aspect('equal')
    ax.axis('off')


def _separar_solapes(pos, radios, iteraciones=400, margen=0.6):
    """
    Empuja las bolitas que se traslapan lejos una de otra hasta que cada
    una tenga su propio espacio, sin alejarlas más de lo necesario de su
    posición real en la cancha.
    """
    coords = {n: list(xy) for n, xy in pos.items()}
    nodos = list(coords.keys())

    for _ in range(iteraciones):
        hubo_ajuste = False
        for i in range(len(nodos)):
            for j in range(i + 1, len(nodos)):
                a, b = nodos[i], nodos[j]
                dx = coords[b][0] - coords[a][0]
                dy = coords[b][1] - coords[a][1]
                dist = (dx ** 2 + dy ** 2) ** 0.5 or 0.001
                min_dist = radios[a] + radios[b] + margen

                if dist < min_dist:
                    empuje = (min_dist - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    coords[a][0] -= ux * empuje
                    coords[a][1] -= uy * empuje
                    coords[b][0] += ux * empuje
                    coords[b][1] += uy * empuje
                    hubo_ajuste = True

        for n in nodos:
            coords[n][0] = min(max(coords[n][0], radios[n] + 1), 120 - radios[n] - 1)
            coords[n][1] = min(max(coords[n][1], radios[n] + 1), 80 - radios[n] - 1)

        if not hubo_ajuste:
            break

    return coords


def graficar_grafo(G, df_scope, titulo, ruta_salida):
    """
    Dibuja el grafo dirigido y ponderado sobre la cancha:
    - Posición del nodo: cerca de la ubicación promedio real del jugador,
      separando las bolitas que se traslapan.
    - Tamaño del nodo: el necesario para que el nombre quepa adentro,
      creciendo además con el volumen de pases del jugador.
    - Grosor y color de arista: proporcional a la cantidad de pases en esa dirección.
    """
    G_corto = _renombrar_corto(G)
    posiciones_reales = calcular_posiciones(df_scope)
    pos_original = {
        NOMBRES_CORTOS.get(j, j): (xy[0], xy[1])
        for j, xy in posiciones_reales.items()
        if NOMBRES_CORTOS.get(j, j) in G_corto.nodes()
    }

    pases_por_nodo = {
        n: sum(d['weight'] for _, _, d in G_corto.out_edges(n, data=True))
         + sum(d['weight'] for _, _, d in G_corto.in_edges(n, data=True))
        for n in G_corto.nodes()
    }
    max_pases = max(pases_por_nodo.values()) if pases_por_nodo else 1
    tam_fuente = 7.5

    # Escala real puntos <-> unidades de cancha: se mide directamente sobre
    # los ejes ya armados (figsize, límites y aspecto fijos), en vez de
    # asumir un factor a ojo. Así el recorte de las flechas en el borde de
    # cada bolita coincide exactamente con lo que se ve en la imagen.
    fig, ax = plt.subplots(figsize=(18, 13))
    _dibujar_cancha(ax)
    ax.set_title(titulo, fontsize=13, fontweight='bold', color='black')
    plt.tight_layout()
    fig.canvas.draw()
    p0 = ax.transData.transform((0, 0))
    p1 = ax.transData.transform((1, 0))
    px_por_dato = abs(p1[0] - p0[0])
    pt_por_dato = px_por_dato / fig.dpi * 72
    dato_por_pt = 1 / pt_por_dato

    # Radio (en unidades de cancha) necesario para que el nombre quepa
    # adentro de la bolita, ajustado además por el volumen de pases.
    radios = {}
    for n in G_corto.nodes():
        ancho_texto_pt = len(n) * tam_fuente * 0.62 + 10
        radio_por_texto = (ancho_texto_pt / 2) * dato_por_pt
        radio_por_pases = 2.3 + 2.2 * (pases_por_nodo[n] / max_pases)
        radios[n] = max(radio_por_texto, radio_por_pases)

    pos = _separar_solapes(pos_original, radios)

    pesos = [d['weight'] for _, _, d in G_corto.edges(data=True)]
    max_peso = max(pesos) if pesos else 1
    anchos = [0.5 + 4.5 * (w / max_peso) for w in pesos]
    cmap = plt.cm.Oranges
    colores = [cmap(0.4 + 0.55 * (w / max_peso)) for w in pesos]

    # node_size que usa NetworkX para recortar las flechas en el borde real
    # de cada bolita (en puntos^2, medido con la escala real calculada arriba).
    tamanos_pt2 = [3.14159 * (radios[n] * pt_por_dato) ** 2 for n in G_corto.nodes()]

    nx.draw_networkx_edges(
        G_corto, pos, ax=ax, width=anchos, edge_color=colores,
        arrows=True, arrowstyle='-|>', arrowsize=14,
        connectionstyle='arc3,rad=0.15',
        min_source_margin=17, min_target_margin=17,
        node_size=tamanos_pt2
    )

    for nodo, (x, y) in pos.items():
        ax.add_patch(patches.Circle(
            (x, y), radios[nodo], facecolor='#F5F5F5',
            edgecolor='#1B1B1B', linewidth=1.5, zorder=3
        ))
        ax.text(
            x, y, nodo, fontsize=tam_fuente, fontweight='bold',
            ha='center', va='center', color='black', zorder=4
        )

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    plt.savefig(ruta_salida, dpi=200)
    plt.close()
