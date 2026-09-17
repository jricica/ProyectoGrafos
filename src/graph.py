"""
Módulo de construcción de grafos con NetworkX.
Requisitos 2 y 3:
- Grafo dirigido (nx.DiGraph): modela la dirección del pase (A -> B).
- Ponderado (weight): cantidad de pases completados entre jugadores.
- Grafo consolidado y grafos individuales por cada partido.
- Métricas de centralidad como apoyo cuantitativo para la interpretación
  futbolística (no exigidas por el enunciado, pero útiles para sostener
  el análisis del estilo de juego).
"""

import networkx as nx
import pandas as pd
from src.cleaning import PARTIDOS


def crear_grafo(df):
    """
    Construye un grafo dirigido y ponderado (nx.DiGraph)
    donde el peso de cada arista es el número de pases completados de A hacia B.
    """
    G = nx.DiGraph()

    conteo = df.groupby(['jugador_nombre', 'receptor_nombre']).agg(
        weight=('resultado', 'count'),
        longitud=('longitud_pase', 'mean')
    ).reset_index()


    for _, fila in conteo.iterrows():
        G.add_edge(
            fila['jugador_nombre'],
            fila['receptor_nombre'],
            weight=int(fila['weight']),
            longitud=round(float(fila['longitud']), 1)
        )

    return G


def crear_grafo_consolidado(df):
    """Construye el grafo consolidado de toda la fase de grupos (3 partidos)."""
    return crear_grafo(df)


def crear_grafos_por_partido(df):
    """
    Construye un diccionario con los 3 grafos individuales por partido:
    {'Uruguay vs Corea del Sur': G1, 'Portugal vs Uruguay': G2, 'Ghana vs Uruguay': G3}
    """
    grafos = {}
    for match_id, nombre_partido in PARTIDOS.items():
        sub_df = df[df['match_id'] == match_id]
        if not sub_df.empty:
            grafos[nombre_partido] = crear_grafo(sub_df)
    return grafos


def obtener_top_conexiones(G, n=10):
    """Retorna las N conexiones dirigidas (A -> B) con mayor cantidad de pases."""
    aristas = []
    for u, v, d in G.edges(data=True):
        aristas.append({
            'Pasador': u,
            'Receptor': v,
            'Pases': d['weight'],
            'Distancia Media (m)': d.get('longitud', 0.0)
        })
    df_conexiones = pd.DataFrame(aristas)
    return df_conexiones.sort_values('Pases', ascending=False).head(n).reset_index(drop=True)


def obtener_sociedades(G, n=5):
    """
    Identifica las parejas de jugadores con mayor intercambio mutuo de balón (A -> B y B -> A).
    Futbolísticamente representa las sociedades más fuertes en la cancha.
    """
    sociedades = []
    visitados = set()

    for u, v in G.edges():
        pareja = tuple(sorted([u, v]))

        if pareja not in visitados and G.has_edge(v, u):
            pases_ida = G[u][v]['weight']
            pases_vuelta = G[v][u]['weight']
            sociedades.append({
                'Jugador 1': pareja[0],
                'Jugador 2': pareja[1],
                'Pases Totales': pases_ida + pases_vuelta
            })
            visitados.add(pareja)

    df_soc = pd.DataFrame(sociedades)
    return df_soc.sort_values('Pases Totales', ascending=False).head(n).reset_index(drop=True)


def resumen_grafo(G):
    """Calcula las métricas estructurales globales del grafo."""
    total_pases = sum(d['weight'] for _, _, d in G.edges(data=True))
    return {
        'nodos': G.number_of_nodes(),
        'aristas': G.number_of_edges(),
        'total_pases': total_pases,
        'densidad': round(nx.density(G), 3)
    }


def calcular_centralidades(G):
    """
    Calcula out-degree, in-degree y betweenness ponderados por jugador,
    como apoyo cuantitativo para la interpretación del estilo de juego.
    """
    out_deg = dict(G.out_degree(weight='weight'))
    in_deg = dict(G.in_degree(weight='weight'))
    betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)

    filas = []
    for jugador in G.nodes():
        filas.append({
            'Jugador': jugador,
            'Pases Dados': out_deg.get(jugador, 0),
            'Pases Recibidos': in_deg.get(jugador, 0),
            'Betweenness': round(betweenness.get(jugador, 0.0), 4)
        })

    df_cent = pd.DataFrame(filas)
    return df_cent.sort_values('Pases Dados', ascending=False).reset_index(drop=True)
