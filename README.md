# ComfyUI-Pitonisa

¡Bienvenido a ComfyUI-Pitonisa! Este repositorio transforma tu ComfyUI en un **motor astrológico profesional** capaz de calcular cartas natales, tránsitos, fases lunares y sinastría, además de generar gráficos astrológicos nativos para usarlos en generación de imágenes.

## 🌟 Nodos Incluidos

El repositorio expone 5 potentes nodos en la categoría `ComfyUI-Pitonisa`:

1.  **Natal Chart Calculator (`NatalChartCalculator`)**
    *   **Propósito:** Calcula la carta astral completa de una persona.
    *   **Salida:** Un JSON en español conteniendo el Sol, la Luna, el Ascendente, la posición de los 10 planetas y de las 12 casas. Ideal para conectar a un nodo de LLM y pedirle que actúe como un astrólogo.

2.  **Transit Data Calculator (`TransitDataCalculator`)**
    *   **Propósito:** Analiza el "cielo actual" o los tránsitos para una fecha y ubicación determinadas.
    *   **Salida:** Un JSON en español que lista en qué signo está cada planeta, y una versión simplificada de la fase lunar (Nueva, Creciente, Llena, Menguante).

3.  **Transit Range Scanner (`TransitRangeScanner`)**
    *   **Propósito:** El escáner temporal para predecir el futuro. Barre un rango de días y detecta cuándo un planeta cambia de signo (ingresos) y cuándo ocurren fases lunares mayores.
    *   **Salida:** Un JSON en español resumiendo los "eventos clave" del periodo. ¡Oro puro para pedirle a un LLM que escriba horóscopos semanales o mensuales!

4.  **Synastry Calculator (`SynastryCalculator`)**
    *   **Propósito:** Calcula la compatibilidad (Sinastría) entre dos personas.
    *   **Salida:** Un JSON en español que destaca los aspectos interplanetarios más importantes (ej. "Sol de P1 en Conjunción con Luna de P2"). Conecta esto a un LLM para consultas de amor y relaciones.

5.  **Natal Chart Image (`NatalChartImageNode`)**
    *   **Propósito:** Generador visual que crea la famosa "rueda zodiacal".
    *   **Salida:** Una **IMAGEN** (Tensor de PyTorch) lista para usarse en ComfyUI. Puedes conectarla a un *Preview Image* para visualizarla, o pasarla por un nodo de ControlNet (Canny/Lineart) para que Stable Diffusion dibuje arte místico basado en la geometría real del usuario.

## 🛠 Instalación

1. Clona o descarga este repositorio en la carpeta `custom_nodes` de tu instalación de ComfyUI.
2. Si utilizas el **ComfyUI Manager**, las dependencias se instalarán automáticamente al reiniciar ComfyUI, ya que hemos incluido el archivo `requirements.txt`.
3. *(Opcional)* Si instalas manualmente, abre la terminal en tu entorno de ComfyUI y ejecuta:
   `pip install -r requirements.txt`

> **Librerías principales:** El motor matemático usa `kerykeion` (en modo offline para rapidez y estabilidad extrema), `geopy` (con Nominatim para resolver ciudades) y `timezonefinder` para el cálculo de zonas horarias. `cairosvg` se encarga de vectorizar la carta astral a píxeles.

## 🚀 Ejemplos de Flujos de Trabajo (Workflows)

Revisa la carpeta `workflows/` de este repositorio. Podrás encontrar plantillas JSON listas para arrastrar y soltar en tu ComfyUI.

*   **Generador de Horóscopo (Texto):** Conecta el `TransitRangeScanner` y tu `NatalChartCalculator` a un nodo LLM (como Ollama). Utiliza un prompt del sistema tipo: *"Eres una pitonisa. Con esta carta natal y estos tránsitos de la semana, redacta una predicción."*
*   **Generador de Arte Místico (Imagen):** Conecta el `NatalChartImageNode` a un `ControlNet Apply` (con modelo Lineart) y pide a tu prompt de Stable Diffusion algo como: *"A beautiful mystical tarot card, golden lines, deep cosmic background..."*
