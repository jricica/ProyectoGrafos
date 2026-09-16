"""
Módulo de carga y limpieza de datos de pases.
Requisito 1: Carga el archivo, filtra la fase de grupos y pases completados,
conservando únicamente las columnas necesarias para el análisis.
"""

import os
import pandas as pd

PARTIDOS = {
    3857287: 'Uruguay vs Corea del Sur',
    3857270: 'Portugal vs Uruguay',
    3857293: 'Ghana vs Uruguay'
}

NOMBRES_CORTOS = {
    'Sergio Rochet Álvarez': 'S. Rochet',
    'Diego Roberto Godín Leal': 'D. Godín',
    'José María Giménez de Vargas': 'J. M. Giménez',
    'Sebastián Coates Nión': 'S. Coates',
    'José Martín Cáceres Silva': 'M. Cáceres',
    'Guillermo Varela Olivera': 'G. Varela',
    'Mathías Olivera Miramontes': 'M. Olivera',
    'Matías Nicolás Viña Susperreguy': 'M. Viña',
    'Federico Santiago Valverde Dipetta': 'F. Valverde',
    'Rodrigo Bentancur Colmán': 'R. Bentancur',
    'Matías Vecino Falero': 'M. Vecino',
    'Giorgian Daniel De Arrascaeta Benedetti': 'De Arrascaeta',
    'Diego Nicolás De La Cruz Arcosa': 'N. De La Cruz',
    'Facundo Pellistri Rebollo': 'F. Pellistri',
    'Agustín Canobbio Graviz': 'A. Canobbio',
    'Darwin Gabriel Núñez Ribeiro': 'D. Núñez',
    'Luis Alberto Suárez Díaz': 'L. Suárez',
    'Edinson Roberto Cavani Gómez': 'E. Cavani',
    'Maximiliano Gómez González': 'M. Gómez'
}


def cargar_datos(ruta='data/pases_uruguay.csv'):
    """Carga el CSV original con soporte UTF-8."""
    if not os.path.exists(ruta):
        ruta = 'Datasets pases FWC 22/pases_uruguay.csv'
    return pd.read_csv(ruta, encoding='utf-8')


def limpiar_datos(df, solo_completos=True):
    """
    Filtra los registros de Fase de Grupos y pases completados,
    conservando únicamente las columnas requeridas por el proyecto.
    """

    df_limpio = df[df['fase'] == 'Group Stage'].copy()
    
    columnas = [
        'fase', 'resultado', 'jugador_nombre', 'receptor_nombre',
        'longitud_pase', 'match_id', 'minuto', 'oponente'
    ]
    df_limpio = df_limpio[columnas].copy()

    df_limpio['jugador_nombre'] = df_limpio['jugador_nombre'].astype(str).str.strip()
    df_limpio['receptor_nombre'] = df_limpio['receptor_nombre'].astype(str).str.strip()
    df_limpio['partido'] = df_limpio['match_id'].map(PARTIDOS)

    if solo_completos:
        df_limpio = df_limpio[df_limpio['resultado'] == 'Complete'].copy()
        df_limpio = df_limpio[df_limpio['receptor_nombre'].notnull()]

    return df_limpio
