"""
Ejecución centralizada del proyecto para evitar problemas y modulación sin comando específico.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cleaning import cargar_datos, limpiar_datos, PARTIDOS
from src.graph import (
    crear_grafo_consolidado,
    crear_grafos_por_partido,
    obtener_top_conexiones,
    obtener_sociedades,
    resumen_grafo,
    calcular_centralidades
)
from src.visualization import graficar_grafo

def print_banner(titulo: str):
    """Imprime un separador visual para cada sección."""
    linea = "=" * 70
    print(f"\n{linea}")
    print(f" {titulo.upper()}")
    print(f"{linea}\n")


def run_step_1():
    print_banner("Paso 1: Carga y Limpieza de Datos")

    raw_df = cargar_datos()
    print(" Archivo CSV cargado exitosamente.")
    print(f"  - Total registros originales: {len(raw_df)}")
    print(f"  - Columnas presentes: {len(raw_df.columns)}")

    df_limpio = limpiar_datos(raw_df, solo_completos=True)
    total_intentados = len(raw_df[raw_df['fase'] == 'Group Stage'])

    print(f"\n Filtros aplicados:")
    print("  - Fase seleccionada: 'Group Stage'")
    print(f"  - Total pases intentados: {total_intentados}")
    print(f"  - Total pases COMPLETADOS: {len(df_limpio)} ({len(df_limpio)/total_intentados*100:.1f}%)")
    print(f"  - Pases fallidos o fuera: {total_intentados - len(df_limpio)}")

    print("\n Distribución de pases completados por partido:")
    for partido in PARTIDOS.values():
        cant = len(df_limpio[df_limpio['partido'] == partido])
        print(f"  * {partido:<26}: {cant:3d} pases completados")

    print(f"\n Plantilla activa de Uruguay:")
    jugadores_unicos = set(df_limpio['jugador_nombre']).union(set(df_limpio['receptor_nombre']))
    print(f"  - Jugadores únicos involucrados en pases: {len(jugadores_unicos)}")
    print(f"  - Distancia promedio de pase: {df_limpio['longitud_pase'].mean():.2f} metros/yardas")

    return df_limpio


def run_step_2(df_clean):
    print_banner("Paso 2: Construcción del Grafo Dirigido y Ponderado")

    print(" Fundamentación del Grafo:")
    print("  * Tipo: Grafo Dirigido (nx.DiGraph).")
    print("  * Ponderación: Pesos (weight = cantidad de pases completados).")
    print("  * Filtrado: Pases completados ('Complete').")

    G_total = crear_grafo_consolidado(df_clean)
    stats = resumen_grafo(G_total)

    print(f"\n Métricas estructurales globales:")
    print(f"  - Nodos (Jugadores): {stats['nodos']}")
    print(f"  - Aristas dirigidas únicas: {stats['aristas']}")
    print(f"  - Pases totales en la red: {stats['total_pases']}")
    print(f"  - Densidad del grafo: {stats['densidad']} (63.7% de conexiones posibles)")

    print("\n Top 10 Conexiones Dirigidas más frecuentes (A -> B):")
    top_edges = obtener_top_conexiones(G_total, n=10)
    print(top_edges.to_string(index=False))

    print("\n Top 5 Sociedades Bilaterales con mayor intercambio (A <-> B):")
    top_pairs = obtener_sociedades(G_total, n=5)
    print(top_pairs.to_string(index=False))

    return G_total


def run_step_3(df_clean):
    print_banner("Paso 3: Grafos Individuales por Partido")

    match_graphs = crear_grafos_por_partido(df_clean)

    for nombre_partido, G_m in match_graphs.items():
        s = resumen_grafo(G_m)
        print(f" {nombre_partido}")
        print(f"  Nodos: {s['nodos']} | Aristas: {s['aristas']} | Pases completados: {s['total_pases']}")
        print("   Top 3 Conexiones:")
        top3 = obtener_top_conexiones(G_m, n=3)
        for _, row in top3.iterrows():
            print(f"     - {row['Pasador']} -> {row['Receptor']}: {row['Pases']} pases (media {row['Distancia Media (m)']}m)")
        print()

def run_step_4(G_total):
    print_banner("Paso 4: Métricas de Centralidad")

    print(" Interpretación de las métricas:")
    print("  * Pases Dados (out-degree)   -> jugadores que más distribuyen el balón.")
    print("  * Pases Recibidos (in-degree) -> jugadores de referencia / puntos de descarga.")
    print("  * Betweenness                -> jugadores que conectan zonas o líneas del equipo.")

    df_cent = calcular_centralidades(G_total)

    print("\n Top 5 por Pases Dados (constructores de juego):")
    print(df_cent.sort_values('Pases Dados', ascending=False).head(5).to_string(index=False))

    print("\n Top 5 por Pases Recibidos (referencias del equipo):")
    print(df_cent.sort_values('Pases Recibidos', ascending=False).head(5).to_string(index=False))

    print("\n Top 5 por Betweenness (conectores / puentes entre líneas):")
    print(df_cent.sort_values('Betweenness', ascending=False).head(5).to_string(index=False))

    return df_cent

def run_step_5(G_total, df_clean):
    print_banner("Paso 5: Visualización del Grafo")

    from src.graph import crear_grafos_por_partido
    from src.cleaning import PARTIDOS

    os.makedirs('output', exist_ok=True)

    graficar_grafo(G_total, df_clean, "Uruguay - Red de Pases (Fase de Grupos)", "output/grafo_consolidado.png")
    print(" Guardado: output/grafo_consolidado.png")

    match_graphs = crear_grafos_por_partido(df_clean)
    for match_id, nombre_partido in PARTIDOS.items():
        if nombre_partido not in match_graphs:
            continue
        df_partido = df_clean[df_clean['match_id'] == match_id]
        archivo = "output/grafo_" + nombre_partido.lower().replace(" ", "_") + ".png"
        graficar_grafo(match_graphs[nombre_partido], df_partido, "Uruguay - Red de Pases: " + nombre_partido, archivo)
        print(f" Guardado: {archivo}")

def main():
    print("=" * 70)
    print(" PROYECTO: ANÁLISIS DE REDES DE PASES - URUGUAY (QATAR 2022)")
    print(" Facultad de Ciencias Económicas | Estructuras de Datos / Grafos° Jimena Estrada y Jan Ricica")
    print("=" * 70)

    df_clean = run_step_1()
    G_total = run_step_2(df_clean)
    run_step_3(df_clean)
    run_step_4(G_total)
    run_step_5(G_total, df_clean)


if __name__ == '__main__':
    main()
