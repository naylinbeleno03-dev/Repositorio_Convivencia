from datetime import date
import os
import pandas as pd
import requests
import streamlit as st

# Crear carpeta para almacenar los documentos firmados si no existe
os.makedirs("documentos_firmados", exist_ok=True)

# Configuración de la página
st.set_page_config(
    page_title="Repositorio Institucional - Convivencia", layout="centered"
)

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    /* 1. Fondo principal en Gris Clarito */
    .stApp {
        background-color: #F3F4F6;
        color: #1F2937;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 2. Barra lateral en Gris un poco más oscuro */
    section[data-testid="stSidebar"] {
        background-color: #475569;
        border-right: 1px solid #334155;
    }

    /* Textos de la barra lateral en blanco */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] a {
        color: #FFFFFF !important;
    }

    /* Visibilidad del desplegable en la barra lateral */
    section[data-testid="stSidebar"] details {
        background-color: #334155 !important;
        border: 1px solid #64748B !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
    }

    section[data-testid="stSidebar"] summary {
        color: #FFFFFF !important;
        background-color: #334155 !important;
        font-weight: 600 !important;
    }

    /* 3. Encabezado superior */
    .header-box {
        background-color: #0F172A;
        padding: 22px;
        border-radius: 12px;
        border-left: 6px solid #D4AF37;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
        margin-bottom: 24px;
    }

    .header-box h1 {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 1.65rem !important;
        font-weight: 600 !important;
    }

    .header-box p {
        color: #E2E8F0 !important;
        margin-top: 6px !important;
        margin-bottom: 0 !important;
        font-size: 0.95rem !important;
    }

    /* Botones generales */
    .stButton>button {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }

    .stButton>button:hover {
        background-color: #D4AF37 !important;
        color: #0F172A !important;
        border-color: #D4AF37 !important;
    }

    /* Campo de entrada de texto */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

    hr {
        border-color: #64748B;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado visual estilizado
st.markdown(
    """
    <div class="header-box">
        <h1>Repositorio Digital de Convivencia Escolar</h1>
        <p>Institución Educativa Técnica Sagrado Corazón.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Configuración de Google Sheets
SHEET_ID = "1eUTG3EFoVvRDpycgNv6JdUP_jAa4106SCCNhXIQGFsc"  # Reemplaza con el ID de tu Google Sheet
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
URL_APPS_SCRIPT = (
    "https://script.google.com/macros/s/AKfycbzyoa-yvvfMj3RE94dGU9tSaPLbo0fRcQs5cfp_QuiB5yUYphukHOj104WWFJ11iSctgQ/exec"  # Reemplaza con la URL de la aplicación web desplegada
)

# Cargar datos directamente desde Google Sheets de forma segura
try:
  df = pd.read_csv(url_csv)
  if "archivo" not in df.columns:
    df["archivo"] = "Sin archivo"
except Exception:
  df = pd.DataFrame(
      columns=[
          "documento",
          "nombre",
          "grado",
          "tipo_registro",
          "detalles",
          "fecha",
          "archivo",
      ]
  )

# 1. Selector de Rol inicial en la barra lateral
st.sidebar.header("Panel de Control")
rol = st.sidebar.selectbox(
    "Seleccione su perfil:",
    ["Estudiante", "Padre de Familia / Acudiente", "Docente / Directivo"],
)

# Sección de enlace al Chatbot en la barra lateral
st.sidebar.markdown("---")
st.sidebar.markdown("### Asistente Virtual")
st.sidebar.markdown(
    "[Abrir Chatbot de"
    " Convivencia](https://chatbot-convivencia-sena-edehd4uhj9lkziarpaexb2.streamlit.app/)"
)

if rol == "Estudiante":
  st.subheader("Portal de Estudiante")
  doc_input = st.text_input(
      "Ingrese su Tarjeta de Identidad o Nombre completo:"
  )

  if doc_input:
    resultado = df[
        df["documento"].astype(str).str.contains(doc_input, case=False, na=False)
        | df["nombre"].str.contains(doc_input, case=False, na=False)
    ]

    if not resultado.empty:
      st.success("Registros encontrados en el sistema:")
      for index, row in resultado.iterrows():
        st.info(
            f" **Fecha:** {row['fecha']} |  **Tipo:**"
            f" {row['tipo_registro']}\n\n**Detalles:** {row['detalles']}"
        )

        # Mostrar botón de descarga si hay un acta firmada adjunta
        nombre_archivo = str(row["archivo"])
        if nombre_archivo and nombre_archivo != "Sin archivo":
          ruta_archivo = os.path.join("documentos_firmados", nombre_archivo)
          if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "rb") as archivo_pdf:
              st.download_button(
                  label=(
                      f"📄 Descargar Acta Firmada Evidencia ({nombre_archivo})"
                  ),
                  data=archivo_pdf,
                  file_name=nombre_archivo,
                  mime="application/octet-stream",
                  key=f"est_{index}",
              )
    else:
      st.warning(
          "No se encontraron registros asociados con ese documento o nombre."
      )

elif rol == "Padre de Familia / Acudiente":
  st.subheader("Portal de Acudiente")
  doc_hijo = st.text_input(
      "Ingrese la Tarjeta de Identidad o Nombre completo del estudiante a su"
      " cargo:"
  )

  if doc_hijo:
    resultado = df[
        df["documento"].astype(str).str.contains(doc_hijo, case=False, na=False)
        | df["nombre"].str.contains(doc_hijo, case=False, na=False)
    ]

    if not resultado.empty:
      st.success("Registros del estudiante:")
      for index, row in resultado.iterrows():
        st.info(
            f" **Estudiante:** {row['nombre']} ({row['grado']})\n"
            f" **Fecha:** {row['fecha']} |  **Tipo:**"
            f" {row['tipo_registro']}\n**Detalles:** {row['detalles']}"
        )

        # Mostrar botón de descarga para acudientes
        nombre_archivo = str(row["archivo"])
        if nombre_archivo and nombre_archivo != "Sin archivo":
          ruta_archivo = os.path.join("documentos_firmados", nombre_archivo)
          if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "rb") as archivo_pdf:
              st.download_button(
                  label=(
                      f"📄 Descargar Acta Firmada Evidencia ({nombre_archivo})"
                  ),
                  data=archivo_pdf,
                  file_name=nombre_archivo,
                  mime="application/octet-stream",
                  key=f"padre_{index}",
              )
    else:
      st.warning("No se hallaron registros para el estudiante indicado.")

elif rol == "Docente / Directivo":
  st.subheader("Panel Administrativo")
  password = st.text_input("Ingrese la contraseña institucional:", type="password")

  # Contraseña configurable
  if password == "Sagracor15*":
    st.success(
        "Acceso concedido. Puede administrar la información del repositorio."
    )

    with st.form("form_agregar"):
      st.write("### Agregar Nuevo Registro al Repositorio")
      nuevo_doc = st.text_input("Documento del Estudiante")
      nuevo_nombre = st.text_input("Nombre Completo")
      nuevo_grado = st.text_input("Grado y Curso")
      tipo_reg = st.selectbox(
          "Tipo de Registro", ["Acta de Compromiso", "Observador de Convivencia"]
      )
      detalles_reg = st.text_area("Descripción de los hechos y compromisos")
      fecha_reg = st.date_input("Fecha", max_value=date.today())

      # Campo para subir el documento escaneado con firmas
      archivo_subido = st.file_uploader(
          "Subir Acta Firmada (PDF, Imagen JPG/PNG)",
          type=["pdf", "png", "jpg", "jpeg"],
      )

      submit = st.form_submit_button("Guardar en el Sistema")

      if submit:
        nombre_archivo_guardado = "Sin archivo"

        # Procesar el archivo si el docente lo subió
        if archivo_subido is not None:
          nombre_archivo_guardado = archivo_subido.name
          ruta_destino = os.path.join(
              "documentos_firmados", nombre_archivo_guardado
          )
          with open(ruta_destino, "wb") as f:
            f.write(archivo_subido.getbuffer())

        # Enviar datos automáticamente a Google Sheets mediante Apps Script
        datos_a_enviar = {
            "documento": nuevo_doc,
            "nombre": nuevo_nombre,
            "grado": nuevo_grado,
            "tipo_registro": tipo_reg,
            "detalles": detalles_reg,
            "fecha": str(fecha_reg),
            "archivo": nombre_archivo_guardado,
        }

        try:
          requests.post(URL_APPS_SCRIPT, json=datos_a_enviar)
          st.success(
              "¡Registro guardado en Google Sheets y documento procesado"
              " exitosamente!"
          )
        except Exception as e:
          st.error(f"Error al conectar con la base de datos en la nube: {e}")

    st.write("---")
    st.write("### Todos los Registros Institucionales")
    st.dataframe(df, use_container_width=True, hide_index=True)

  elif password:
    st.error("Contraseña incorrecta. Intente de nuevo.")
