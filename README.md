# Proyecto de Grafos - Estilo de Juego (Uruguay, Qatar 2022)

Análisis de la red de pases de Uruguay en la fase de grupos del Mundial Qatar 2022, usando NetworkX.

## Cómo correrlo

```bash
pip3 install -r requirements.txt
python3 manage.py
```

Esto imprime en consola la limpieza de datos, la construcción del grafo, las métricas de centralidad, y genera 4 imágenes en `output/` (el grafo consolidado y uno por cada partido).

## El grafo

- **Dirigido y ponderado:** cada arista va de quien da el pase a quien lo recibe, con peso = cantidad de pases completados entre ambos.
- **Alcance:** un grafo consolidado con los 3 partidos de fase de grupos, y uno por partido.
- **Pases considerados:** solo los completados.
- **Visualización:** los jugadores se ubican en su posición promedio real en la cancha (calculada con las coordenadas de cada pase), no en un layout automático.

## Interpretación

### Cómo jugó Uruguay en la fase de grupos (según el grafo de pases)

Los que más tocaron el balón durante los 3 partidos fueron **Valverde**, **Giménez** y **Bentancur**, no los delanteros. **Suárez**, **Cavani** y **Núñez** casi no aparecen recibiendo o dando pases en el grafo. O sea que el balón se quedaba mucho entre los mismos jugadores de atrás y de en medio de la cancha, y no llegaba tanto a los que tenían que meter el gol.

Esto puede explicar por qué a Uruguay le costó tanto anotar en ese Mundial: el equipo se pasaba el balón entre ellos con calma, pero no encontraba la forma de hacerlo llegar a los delanteros. Al final quedaron eliminados en la fase de grupos aunque no perdieron feo ningún partido, lo cual coincide con esto.

Las combinaciones de jugadores que más se repitieron pasándose el balón (Valverde-Bentancur, Valverde-Giménez, Godín-Cáceres) también son puros jugadores de defensa o de en medio, ninguno de ataque.

### Comparando los 3 partidos

El patrón cambia un poco según el rival. Contra Corea del Sur (0-0) los que más se pasaron el balón fueron los defensas (Cáceres, Godín, Giménez), como si el equipo se hubiera quedado tranquilo pasándoselo entre ellos atrás. Contra Portugal (0-2, la peor derrota) ya no fueron tanto los defensas, sino Bentancur y Valverde los que más conectaron. Y contra Ghana (2-0, el partido en el que quedaron eliminados) Valverde fue otra vez el que más tocó el balón, conectando con los jugadores de las bandas (Varela y Coates), quizás porque necesitaban ganar sí o sí y buscaron moverse más por los lados de la cancha.

## Autores

Jimena Estrada y Jan Ricica
