import json
import fitz  # PyMuPDF
from PIL import Image
import io
import os

# ============================================================================
# CONFIGURACIÓN DE COORDENADAS PARA LA TABLA DE FIRMAS
# ============================================================================
# Estas son las posiciones verticales (línea base) para cada una de las 16 filas de la tabla.
FILAS_Y = [
    433.75, 453.79, 473.95, 493.99, 514.03, 534.07, 555.19, 576.67,
    596.71, 617.86, 638.86, 659.98, 680.98, 701.98, 723.10, 744.10
]

# X base para el nombre (columna izquierda)
X_NOMBRE = 98

# Límites de la columna de firmas (columna derecha)
X0_FIRMA = 382
X1_FIRMA = 531

def procesar_firma(ruta_imagen):
    """
    Abre una imagen de firma, recorta todos los bordes transparentes extra,
    la comprime manteniendo su relación de aspecto y retorna los bytes.
    """
    try:
        img = Image.open(ruta_imagen)
        
        # Recortar el exceso de transparencia (muy común en imágenes removebg)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
            alpha = img.split()[-1] # Obtener solo el canal de opacidad
            bbox = alpha.getbbox()  # Encontrar los límites de lo que NO es transparente
            if bbox:
                img = img.crop(bbox)
        
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
        
    except FileNotFoundError:
        print(f"  [Advertencia] Imagen (Firma) no encontrada: {ruta_imagen}")
        return None
    except Exception as e:
        print(f"  [Error] Procesando la firma {ruta_imagen}: {e}")
        return None

def generar_nombramientos(json_path, pdf_template_path, output_pdf_path):
    print("Iniciando generación de firmas...")
    
    if not os.path.exists(json_path):
        print(f"Error: El archivo JSON '{json_path}' no existe.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    personas = data.get("players", [])
    if not personas:
        print("No se encontraron personas en el archivo JSON.")
        return
        
    print(f"Total de personas a procesar: {len(personas)}")

    if not os.path.exists(pdf_template_path):
        print(f"Error: La plantilla PDF '{pdf_template_path}' no existe en esta carpeta.")
        return
        
    doc_template = fitz.open(pdf_template_path)
    if len(doc_template) == 0:
        print("Error: La plantilla PDF parece estar vacía.")
        return

    doc_out = fitz.open()
    
    font_size = 11
    font_color = (0, 0, 0) # Negro

    # Agrupar en bloques de 16 (porque la tabla tiene 16 filas por página)
    chunks = [personas[i:i + 16] for i in range(0, len(personas), 16)]

    for chunk_idx, chunk in enumerate(chunks):
        print(f"Procesando página {chunk_idx + 1}...")
        
        # Clonar la primera página de la plantilla
        doc_out.insert_pdf(doc_template, from_page=0, to_page=0)
        page = doc_out[-1]
        
        for idx, persona in enumerate(chunk):
            y_base = FILAS_Y[idx]
            
            # --- Insertar Textos (Nombre) ---
            name = persona.get("name", "")
            if name:
                # El texto se escribe ligeramente arriba de la línea base
                page.insert_text(
                    fitz.Point(X_NOMBRE, y_base), 
                    name, 
                    fontsize=font_size, 
                    color=font_color
                )
            
            # --- Insertar Firma ---
            file_path = persona.get("file")
            if file_path:
                # Zig-Zag: 
                # Las filas pares se desplazan a la izquierda, las impares a la derecha
                if idx % 2 == 0:
                    x0_firma = X0_FIRMA - 15  # Desplazar hacia la izquierda
                    x1_firma = X1_FIRMA - 45  
                else:
                    x0_firma = X0_FIRMA + 45  # Desplazar hacia la derecha
                    x1_firma = X1_FIRMA + 15
                
                # Damos más espacio vertical a la firma para que luzca grande y natural.
                # Las firmas grandes pueden "pasarse" de su renglón un poquito (muy realista).
                rect_firma_coord = {
                    "x0": x0_firma, 
                    "y0": y_base - 22,   # Subimos un poco el techo
                    "x1": x1_firma, 
                    "y1": y_base + 8     # Bajamos un poco el piso
                }
                
                img_bytes = procesar_firma(file_path)
                if img_bytes:
                    rect_firma = fitz.Rect(
                        rect_firma_coord["x0"], rect_firma_coord["y0"], 
                        rect_firma_coord["x1"], rect_firma_coord["y1"]
                    )
                    # keep_proportion=True evitará que se deforme
                    page.insert_image(rect_firma, stream=img_bytes, keep_proportion=True)

    doc_out.save(output_pdf_path)
    doc_out.close()
    doc_template.close()
    print(f"\n¡Éxito! PDF generado y guardado como: {output_pdf_path}")

if __name__ == "__main__":
    # Nombres de archivos configurados para la carpeta actual
    JSON_FILE = "datos.json"
    TEMPLATE_FILE = "NOMBRAMIENTO TORNEO DE BARRIOS.pdf"
    OUTPUT_FILE = "nombramientos_finales.pdf"
    
    # Asegurarnos de trabajar en el directorio correcto
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    generar_nombramientos(JSON_FILE, TEMPLATE_FILE, OUTPUT_FILE)
