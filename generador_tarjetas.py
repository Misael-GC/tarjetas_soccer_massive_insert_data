import json
import fitz  # PyMuPDF
from PIL import Image
import io
import os

# ============================================================================
# CONFIGURACIÓN DE COORDENADAS
# ============================================================================
# Esta lista contiene 8 diccionarios (uno para cada posición de tarjeta en la página).
# Cada tarjeta en la plantilla PDF (2 columnas x 4 filas) necesita sus coordenadas.
# (0,0) es la esquina superior izquierda de la página.
# Tendrás que ajustar estos valores midiendo tu PDF (TARGETAS 2024-2027.pdf).
# Puedes usar herramientas online como PDF coordinate finder o medir en Acrobat.

POSICIONES = [
    {
        "foto": {"x0": 50, "y0": 50, "x1": 150, "y1": 150},
        "nombre": {"x": 50, "y": 170},
        "equipo": {"x": 50, "y": 190},
        "categoria": {"x": 50, "y": 210}
    },
    {
        "foto": {"x0": 250, "y0": 50, "x1": 350, "y1": 150},
        "nombre": {"x": 250, "y": 170},
        "equipo": {"x": 250, "y": 190},
        "categoria": {"x": 250, "y": 210}
    },
    {
        "foto": {"x0": 50, "y0": 250, "x1": 150, "y1": 350},
        "nombre": {"x": 50, "y": 370},
        "equipo": {"x": 50, "y": 390},
        "categoria": {"x": 50, "y": 410}
    },
    {
        "foto": {"x0": 250, "y0": 250, "x1": 350, "y1": 350},
        "nombre": {"x": 250, "y": 370},
        "equipo": {"x": 250, "y": 390},
        "categoria": {"x": 250, "y": 410}
    },
    {
        "foto": {"x0": 50, "y0": 450, "x1": 150, "y1": 550},
        "nombre": {"x": 50, "y": 570},
        "equipo": {"x": 50, "y": 590},
        "categoria": {"x": 50, "y": 610}
    },
    {
        "foto": {"x0": 250, "y0": 450, "x1": 350, "y1": 550},
        "nombre": {"x": 250, "y": 570},
        "equipo": {"x": 250, "y": 590},
        "categoria": {"x": 250, "y": 610}
    },
    {
        "foto": {"x0": 50, "y0": 650, "x1": 150, "y1": 750},
        "nombre": {"x": 50, "y": 770},
        "equipo": {"x": 50, "y": 790},
        "categoria": {"x": 50, "y": 810}
    },
    {
        "foto": {"x0": 250, "y0": 650, "x1": 350, "y1": 750},
        "nombre": {"x": 250, "y": 770},
        "equipo": {"x": 250, "y": 790},
        "categoria": {"x": 250, "y": 810}
    }
]

def procesar_imagen_cuadrada(ruta_imagen, coords_destino):
    """
    Abre una imagen, la recorta desde el centro manteniendo un aspect ratio 
    perfectamente cuadrado (o el que dicten las coordenadas si no fuera exacto)
    sin deformarla, y retorna los bytes comprimidos para insertar en el PDF.
    """
    try:
        img = Image.open(ruta_imagen)
        width, height = img.size
        
        # Calcular el lado del cuadrado ideal (tomamos el lado más corto para no perder imagen)
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        
        # Recorte cuadrado perfecto desde el centro
        img_cropped = img.crop((left, top, right, bottom))
        
        # Opcional: Redimensionar según tamaño destino para no inflar el PDF
        w_pts = coords_destino["x1"] - coords_destino["x0"]
        h_pts = coords_destino["y1"] - coords_destino["y0"]
        
        # Ajustar multiplicando por un factor (ej. x3) para buena resolución en impresión
        target_size = (int(w_pts * 3), int(h_pts * 3))
        
        # Convertir a RGB si tiene canal Alpha (transparencia) para guardarlo como JPEG
        if img_cropped.mode in ("RGBA", "P"):
            img_cropped = img_cropped.convert("RGB")
            
        img_resized = img_cropped.resize(target_size, Image.Resampling.LANCZOS)
        
        img_byte_arr = io.BytesIO()
        img_resized.save(img_byte_arr, format='JPEG', quality=90)
        return img_byte_arr.getvalue()
        
    except FileNotFoundError:
        print(f"  [Advertencia] Imagen no encontrada: {ruta_imagen}")
        return None
    except Exception as e:
        print(f"  [Error] Procesando la imagen {ruta_imagen}: {e}")
        return None

def generar_tarjetas(json_path, pdf_template_path, output_pdf_path):
    print("Iniciando generación de tarjetas...")
    
    # 1. Cargar datos del JSON
    if not os.path.exists(json_path):
        print(f"Error: El archivo JSON '{json_path}' no existe.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    players = data.get("players", [])
    if not players:
        print("No se encontraron jugadores en el archivo JSON.")
        return
        
    print(f"Total de jugadores cargados: {len(players)}")

    # 2. Abrir la plantilla PDF
    if not os.path.exists(pdf_template_path):
        print(f"Error: La plantilla PDF '{pdf_template_path}' no existe.")
        return
        
    doc_template = fitz.open(pdf_template_path)
    if len(doc_template) == 0:
        print("Error: La plantilla PDF parece estar vacía.")
        return

    # 3. Crear documento de salida
    doc_out = fitz.open()

    # 4. Agrupar jugadores en chunks (grupos) de 8
    chunks = [players[i:i + 8] for i in range(0, len(players), 8)]
    
    # Configuraciones de texto
    font_size = 11
    font_color = (0, 0, 0) # Negro. Para RGB en PyMuPDF se usa rango 0.0 a 1.0, pero PyMuPDF acepta tuplas RGB (0,0,0)

    for chunk_index, chunk in enumerate(chunks):
        print(f"Procesando página {chunk_index + 1}...")
        
        # Insertar una copia de la página 0 de la plantilla en el documento de salida
        doc_out.insert_pdf(doc_template, from_page=0, to_page=0)
        page = doc_out[-1] # Seleccionar la última página agregada
        
        for idx, player in enumerate(chunk):
            pos = POSICIONES[idx]
            print(f"  -> Insertando datos de: {player.get('name', 'Desconocido')} (Posición {idx+1})")
            
            # --- Insertar Imagen ---
            file_path = player.get("file")
            if file_path:
                img_bytes = procesar_imagen_cuadrada(file_path, pos["foto"])
                if img_bytes:
                    rect_foto = fitz.Rect(pos["foto"]["x0"], pos["foto"]["y0"], pos["foto"]["x1"], pos["foto"]["y1"])
                    # keep_proportion=False obliga a rellenar el rectángulo, pero como ya recortamos la foto 
                    # de forma cuadrada en PIL, se ajustará perfectamente sin deformarse.
                    page.insert_image(rect_foto, stream=img_bytes, keep_proportion=False)
            
            # --- Insertar Textos ---
            name = player.get("name", "")
            team = player.get("team", "")
            category = player.get("category", "")
            
            if name:
                page.insert_text(fitz.Point(pos["nombre"]["x"], pos["nombre"]["y"]), name, fontsize=font_size, color=font_color)
            if team:
                page.insert_text(fitz.Point(pos["equipo"]["x"], pos["equipo"]["y"]), team, fontsize=font_size, color=font_color)
            if category:
                page.insert_text(fitz.Point(pos["categoria"]["x"], pos["categoria"]["y"]), category, fontsize=font_size, color=font_color)

    # 5. Guardar documento final
    doc_out.save(output_pdf_path)
    doc_out.close()
    doc_template.close()
    print(f"\n¡Éxito! PDF generado y guardado como: {output_pdf_path}")

if __name__ == "__main__":
    # Nombres de archivos según el contexto
    JSON_FILE = "data.json"
    TEMPLATE_FILE = "TARGETAS 2024-2027.pdf"
    OUTPUT_FILE = "tarjetas_finales.pdf"
    
    generar_tarjetas(JSON_FILE, TEMPLATE_FILE, OUTPUT_FILE)
