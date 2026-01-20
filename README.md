# ⚽ La Pelotona - Partidos de Hoy

Proyecto automatizado que extrae información de partidos de fútbol desde [La Pelotona](https://www.lapelotona.com/pe/partidos-hoy/), la almacena en Google Sheets y genera una página HTML limpia para visualización.

## 📋 Descripción

Este proyecto realiza las siguientes tareas de forma automática:

1. **Descarga** el HTML de la página web de La Pelotona
2. **Extrae** la información de los partidos (equipos, hora, canal)
3. **Sube** los datos a un documento de Google Sheets
4. **Genera** una página HTML limpia y responsive con los partidos
5. **Publica** automáticamente en GitHub Pages

## 🗂️ Estructura del Proyecto

```
LaPelotona/
├── .github/
│   └── workflows/
│       └── main.yml          # Workflow de GitHub Actions
├── script.py                 # Script principal de Python
├── requirements.txt          # Dependencias de Python
├── pagina_original.html      # HTML original descargado de la web
├── lapelotona.html           # HTML limpio generado con los partidos
└── README.md                 # Este archivo
```

## 🔧 Archivos Principales

### `script.py`
Script principal que realiza todo el proceso:
- Descarga el contenido de la web y lo guarda en `pagina_original.html`
- Extrae los partidos usando BeautifulSoup
- Sube los datos a Google Sheets con formato y colores
- Genera `lapelotona.html` con un diseño limpio y responsive

### `main.yml`
Workflow de GitHub Actions que:
- Ejecuta el script automáticamente según el horario programado
- Sube los archivos HTML actualizados al repositorio
- Permite ejecución manual desde la pestaña Actions

## ⏰ Horario de Ejecución

El script se ejecuta automáticamente todos los días a las **6:00 a.m. hora de Perú** (11:00 UTC).

También puede ejecutarse manualmente desde GitHub:
1. Ir a la pestaña **Actions**
2. Seleccionar **"Ejecutar script LaPelotona"**
3. Clic en **"Run workflow"** → Seleccionar rama `main` → Confirmar

## 🌐 Visualización

La página con los partidos está disponible en GitHub Pages:

```
https://gustavoalcantarag.github.io/LaPelotona/lapelotona.html
```

## 📊 Google Sheets

Los datos también se almacenan en un documento de Google Sheets con:
- Fecha y hora de actualización
- Partidos organizados por día
- Formato con colores para mejor visualización

## 🔐 Configuración de Secrets

El proyecto requiere los siguientes secrets configurados en GitHub:

### Credenciales de Google Sheets
| Secret | Descripción |
|--------|-------------|
| `CRED_TYPE` | Tipo de credencial |
| `CRED_PROJECT_ID` | ID del proyecto de Google Cloud |
| `CRED_PRIVATE_KEY_ID` | ID de la clave privada |
| `CRED_PRIVATE_KEY` | Clave privada del service account |
| `CRED_CLIENT_EMAIL` | Email del service account |
| `CRED_CLIENT_ID` | ID del cliente |
| `CRED_AUTH_URI` | URI de autenticación |
| `CRED_TOKEN_URI` | URI del token |
| `CRED_AUTH_PROVIDER_X509_CERT_URL` | URL del certificado del proveedor |
| `CRED_CLIENT_X509_CERT_URL` | URL del certificado del cliente |
| `CRED_UNIVERSE_DOMAIN` | Dominio del universo |

## 📦 Dependencias

Las dependencias del proyecto están en `requirements.txt`:
- `requests` - Para descargar contenido web
- `beautifulsoup4` - Para parsear HTML
- `gspread` - Para interactuar con Google Sheets
- `google-auth` - Autenticación con Google
- `gspread-formatting` - Formato de celdas en Google Sheets
- `pytz` - Manejo de zonas horarias

## 🚀 Instalación Local (Opcional)

Si deseas ejecutar el script localmente:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/gustavoalcantarag/LaPelotona.git
   cd LaPelotona
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   pip install pytz
   ```

3. Configura las variables de entorno con las credenciales de Google

4. Ejecuta el script:
   ```bash
   python script.py
   ```

## 📝 Flujo del Proceso

```
┌─────────────────────────────────────────────────────────────────┐
│                    EJECUCIÓN DEL SCRIPT                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Descargar HTML de https://www.lapelotona.com/pe/partidos-hoy│
│     └─> Guardar en: pagina_original.html                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Extraer datos de partidos                                   │
│     └─> Equipos, Hora, Canal (agrupados por día)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Subir datos a Google Sheets                                 │
│     └─> Con formato y colores                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Generar HTML limpio                                         │
│     └─> Guardar en: lapelotona.html                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Subir archivos a GitHub                                     │
│     └─> pagina_original.html + lapelotona.html                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. GitHub Pages se actualiza automáticamente                   │
│     └─> Disponible en: .github.io/LaPelotona/lapelotona.html    │
└─────────────────────────────────────────────────────────────────┘
```

## 👤 Autor

**Gustavo Alcántara**

---

*Última actualización: Enero 2026*
