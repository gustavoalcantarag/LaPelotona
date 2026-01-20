from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime


import pytz
tz = pytz.timezone('America/Lima')
now = datetime.now(tz)
import requests
from bs4 import BeautifulSoup
import csv
import os
import json
from datetime import datetime

# Cargar credenciales desde variables de entorno
def get_credentials_from_env():
    return {
        "type": os.environ.get("CRED_TYPE"),
        "project_id": os.environ.get("CRED_PROJECT_ID"),
        "private_key_id": os.environ.get("CRED_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("CRED_PRIVATE_KEY"),
        "client_email": os.environ.get("CRED_CLIENT_EMAIL"),
        "client_id": os.environ.get("CRED_CLIENT_ID"),
        "auth_uri": os.environ.get("CRED_AUTH_URI"),
        "token_uri": os.environ.get("CRED_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("CRED_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("CRED_CLIENT_X509_CERT_URL"),
        "universe_domain": os.environ.get("CRED_UNIVERSE_DOMAIN")
    }

# Si necesitas las credenciales como dict
credentials = get_credentials_from_env()
## Si necesitas como json string: json.dumps(credentials)
fecha_hora = now.strftime("%A, %d %B %Y - %H:%M:%S")

try:
    url = "https://www.lapelotona.com/pe/partidos-hoy/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    # Guardar el HTML original (opcional, para debug)
    with open("pagina_original.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Descarga y guardado de HTML original completado.")
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
## ...existing code...
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

try:

    # Autenticación con Google Sheets usando credenciales desde variables de entorno
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(credentials, scopes=scopes)
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

# --- Generar HTML limpio con los datos extraídos ---
try:
    html_limpio = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Partidos de Hoy - La Pelotona</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .fecha-actualizacion {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .seccion {
            background-color: white;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .titulo-dia {
            background-color: #4a90d9;
            color: white;
            padding: 12px 15px;
            font-weight: bold;
            font-size: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background-color: #e8f0fe;
            padding: 10px 15px;
            text-align: left;
            font-weight: bold;
            color: #333;
        }
        td {
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }
        tr:last-child td {
            border-bottom: none;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>⚽ Partidos de Hoy</h1>
"""
    # Agregar fecha de actualización
    html_limpio += f'    <p class="fecha-actualizacion">Actualizado: {fecha_hora}</p>\n'
    
    # Agregar cada sección (día) con sus partidos
    for seccion in secciones[1:]:  # Saltar la primera sección que es solo la fecha
        titulo_dia = seccion[0][0] if seccion[0] else ""
        html_limpio += f'''    <div class="seccion">
        <div class="titulo-dia">{titulo_dia}</div>
        <table>
            <tr>
                <th>Equipos</th>
                <th>Hora / Canal</th>
            </tr>
'''
        for partido in seccion[2:]:  # Saltar título y encabezado
            equipos = partido[0] if len(partido) > 0 else ""
            hora_canal = partido[1] if len(partido) > 1 else ""
            html_limpio += f'''            <tr>
                <td>{equipos}</td>
                <td>{hora_canal}</td>
            </tr>
'''
        html_limpio += '''        </table>
    </div>
'''
    
    html_limpio += """</body>
</html>"""
    
    # Guardar el HTML limpio
    with open("pagina.html", "w", encoding="utf-8") as f:
        f.write(html_limpio)
    
    print("HTML limpio generado correctamente en pagina.html")
except Exception as e:
    print(f"Error generando HTML limpio: {e}")
    raise