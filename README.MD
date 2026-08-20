# Generador Automático de Tarjetas Deportivas

Este proyecto contiene un script en Python diseñado para automatizar la creación de credenciales o tarjetas deportivas. El script toma datos estructurados desde un archivo JSON y fotografías locales, y los inyecta dinámicamente sobre una plantilla PDF preexistente.

## 📝 Características
- **Paginación Dinámica:** La plantilla base tiene capacidad para 8 tarjetas por página (formato 2x4). Si hay más de 8 jugadores, el script duplica automáticamente la plantilla y crea nuevas páginas en el mismo documento de salida para evitar sobrescribir datos.
- **Auto-Ajuste de Fotografías:** Recorta las imágenes desde el centro para asegurar que sean perfectamente cuadradas (o coincidan con el aspecto del destino) antes de insertarlas, evitando que los rostros se deformen o achaten.
- **Tolerancia a Datos Faltantes:** Si un jugador no tiene registrado un equipo o categoría, el script dejará los campos en blanco sin detener la ejecución.

---

## 🛠️ Requisitos Previos

Necesitas tener instalado **Python 3.x** en tu sistema. Además, el script depende de dos librerías externas para la manipulación de imágenes y del PDF.

### Instalación de dependencias
Abre tu terminal o símbolo del sistema y ejecuta el siguiente comando:

```bash
pip install PyMuPDF Pillow
```

---

## 📁 Estructura de Archivos Necesaria

Para que el script funcione correctamente, asegúrate de tener los siguientes archivos en la misma carpeta:

1. `generador_tarjetas.py`: El script principal de Python.
2. `TARGETAS 2024-2027.pdf`: La plantilla PDF base con las 8 tarjetas en blanco.
3. `jugadores.json`: Archivo con la información de los jugadores.
4. **Imágenes**: Las fotografías de los jugadores referenciadas en el JSON.

### Estructura esperada de `jugadores.json`
El JSON debe contener un arreglo llamado `players`. Cada objeto debe tener, como mínimo, el nombre del jugador y la ruta a su foto.

```json
{
    "players": [
        { 
            "name": "Misael Gómez Cuautle",
            "file": "./Misael Gomez Cuautle.jpeg",
            "team": "La Masía",
            "category": "Libre"
        },
        {
            "name": "Alan Coyopotl Solis",
            "file": "./Alan Coyopotl Solis.jpeg"
        }
    ]
}
```

---

## 🚀 Cómo Ejecutarlo

Una vez que tengas tu `data.json` con los datos listos y las dependencias instaladas, ejecuta el script desde tu terminal ubicándote en la carpeta del proyecto:

```bash
python generador_tarjetas.py
```

Al finalizar, el script habrá generado un nuevo archivo llamado **`tarjetas_finales.pdf`** con todas las credenciales listas para imprimir.

---

## ⚙️ Configuración Avanzada (Coordenadas)

Si en el futuro la plantilla PDF cambia de tamaño o las cajas se mueven, puedes ajustar las posiciones abriendo `generador_tarjetas.py` con cualquier editor de texto. 

En las primeras líneas encontrarás un arreglo llamado `POSICIONES`. Este arreglo contiene 8 bloques (uno por cada cuadrante de la hoja). Puedes ajustar los valores `x` (horizontal) y `y` (vertical) al milímetro para alinear perfectamente los textos y fotografías sobre la nueva plantilla.
