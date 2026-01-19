import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime


now = datetime.now()
fecha_hora = now.strftime("%A, %d %B %Y - %H:%M:%S")

# Siempre eliminar y descargar el HTML más reciente
try:
    if os.path.exists("pagina.html"):
        os.remove("pagina.html")
    url = "https://www.lapelotona.com/pe/partidos-hoy/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    with open("pagina.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Descarga y guardado de HTML completado.")
except Exception as e:
    print(f"Error descargando HTML: {e}")
    raise

soup = BeautifulSoup(html, "html.parser")

# Extraer partidos agrupados por día y preparar formato de secciones
secciones = []  # Cada sección es una lista de filas (incluyendo encabezado de día y encabezado de columnas)
current_day = None
partidos_dia = []
# Agregar fila con fecha y hora de ejecución (ocupa dos columnas)
secciones.append([[fecha_hora, ""]])
try:
    for elem in soup.find_all(['h2', 'div'], recursive=True):
        if elem.name == 'h2' and 'Partidos' in elem.get_text():
            # Si ya hay partidos acumulados, guardar la sección anterior
            if current_day and partidos_dia:
                secciones.append([ [current_day], ["EQUIPOS", "HORA/CANAL"] ] + partidos_dia)
                partidos_dia = []
            current_day = elem.get_text(strip=True)
        elif elem.name == 'div' and 'partidos-tabla' in elem.get('class', []):
            table = elem.find("table", class_="views-table")
            if not table or not current_day:
                continue
            for row in table.find_all("tr"):
                equipos_td = row.find("td", class_="equipos")
                fecha_td = row.find("td", class_="fecha")
                if equipos_td and fecha_td:
                    equipos = " vs ".join([span.get_text(strip=True) for span in equipos_td.find_all("span")])
                    hora_span = fecha_td.find("span", class_="usa-time")
                    hora = hora_span.get_text(strip=True) if hora_span else ""
                    canal = fecha_td.get_text(separator=" ", strip=True).replace(hora, "").strip()
                    hora_canal = f"{hora} {canal}".strip()
                    partidos_dia.append([equipos, hora_canal])
    # Agregar la última sección si hay partidos pendientes
    if current_day and partidos_dia:
        secciones.append([ [current_day], ["EQUIPOS", "HORA/CANAL"] ] + partidos_dia)
    print("Extracción y agrupación de partidos completada.")
except Exception as e:
    print(f"Error extrayendo partidos: {e}")
    raise



# --- Subir datos a Google Sheets ---
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import CellFormat, Color, format_cell_ranges

GOOGLE_SHEET_ID = "1WuVGh7PrfnTSXHnL40YG_P48HbavZKSKxCkKtLdN8V4"
RANGO_HOJA = "A1"  # Comenzar en la celda A1
NOMBRE_CRED = "credenciales.json"  # Nombre del archivo de credenciales

try:
    # Autenticación con Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(NOMBRE_CRED, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sh.sheet1  # Usa la primera hoja

    # Borra el contenido anterior (opcional)
    worksheet.clear()

    # Limpiar todos los colores de fondo antes de escribir
    from gspread_formatting import CellFormat, Color, format_cell_range
    formato_blanco = CellFormat(backgroundColor=Color(1, 1, 1))  # Fondo blanco
    format_cell_range(worksheet, 'A1:J1000', formato_blanco)

    # Preparar los valores para Google Sheets en el nuevo formato
    valores = []
    filas_titulo = []  # Guardar los índices de las filas de título y encabezado
    fila_actual = 1
    # Agregar la fila de fecha/hora (primera fila)
    valores.append(secciones[0][0])
    filas_titulo.append(fila_actual)  # También darle color
    fila_actual += 1
    # Agregar una fila vacía debajo de la fecha/hora
    valores.append(["", ""])
    fila_actual += 1
    # Agregar el resto de secciones
    for seccion in secciones[1:]:
        # Fila de título de día
        valores.append(seccion[0])
        filas_titulo.append(fila_actual)
        fila_actual += 1
        # Fila de encabezado
        valores.append(seccion[1])
        filas_titulo.append(fila_actual)
        fila_actual += 1
        # Partidos
        for fila in seccion[2:]:
            valores.append(fila)
            fila_actual += 1
        valores.append([""])
        fila_actual += 1
    # Eliminar la última línea en blanco si existe
    if valores and (valores[-1] == [""] or valores[-1] == ["", ""]):
        valores.pop()
        fila_actual -= 1
    # Calcular rango dinámico
    col_count = max(len(fila) for fila in valores)
    end_col = chr(ord('A') + col_count - 1)
    worksheet.update(range_name=f'A1:{end_col}{len(valores)}', values=valores)

    # Formato: color de fondo para filas de fecha/hora, título y encabezado (excepto filas vacías)
    from gspread_formatting import CellFormat, Color, format_cell_ranges
    formato_titulo = CellFormat(backgroundColor=Color(0.8, 0.9, 1))  # Azul claro
    rango_formato = []
    for fila in filas_titulo:
        # Solo aplicar formato si la fila no es vacía
        if any(cell.strip() for cell in valores[fila-1]):
            rango = f'A{fila}:{end_col}{fila}'
            rango_formato.append((rango, formato_titulo))
    if rango_formato:
        format_cell_ranges(worksheet, rango_formato)

    print("Datos subidos a Google Sheets correctamente (formato por secciones, color en títulos y sin color en filas vacías).")
except Exception as e:
    print(f"Error subiendo a Google Sheets: {e}")
    raise