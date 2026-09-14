import base64
from datetime import date, datetime
import os
import pandas as pd
import requests
import streamlit as st
from zoneinfo import ZoneInfo

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
SHEET_ID = "1eUTG3EFoVvRDpycgNv6JdUP_jAa4106SCCNhXIQGFsc"
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxDuN5qazL_uB1zpSu0TJ7Y0mvD6HmMzByPraF4J36a3pmj6aJzJzIbkIIWI6MOMhnRoQ/exec"

# Cargar datos en la memoria de sesión para asegurar actualización instantánea
if "df" not in st.session_state:
  try:
    df_temp = pd.read_csv(url_csv)
    df_temp.columns = [str(col).strip().lower() for col in df_temp.columns]
    if "archivo" not in df_temp.columns:
      df_temp["archivo"] = "Sin archivo"
    st.session_state.df = df_temp
  except Exception:
    st.session_state.df = pd.DataFrame(
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

df = st.session_state.df

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


# Función para mostrar el botón interactivo que abre el documento de Google Drive
def mostrar_evidencia(link_archivo):
  if link_archivo and str(link_archivo).strip() not in [
      "Sin archivo",
      "nan",
      "None",
      "",
  ]:
    st.markdown("---")
    if str(link_archivo).startswith("http"):
      st.markdown("**📄 Evidencia o Acta Firmada en la Nube:**")
      st.link_button(
          "🔗 Abrir y Ver Documento Firmado",
          link_archivo,
          use_container_width=True,
      )
    else:
      st.info(f"📄 Archivo registrado: `{link_archivo}`")


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
        mostrar_evidencia(row["archivo"])
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
        mostrar_evidencia(row["archivo"])
    else:
      st.warning("No se hallaron registros para el estudiante indicado.")

elif rol == "Docente / Directivo":
  st.subheader("Panel Administrativo")
  password = st.text_input("Ingrese la contraseña institucional:", type="password")

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

      # Fecha actual exacta ajustada a Colombia (evita que se adelante al día siguiente)
      hoy_colombia = datetime.now(ZoneInfo("America/Bogota")).date()
      fecha_reg = st.date_input(
          "Fecha", value=hoy_colombia, max_value=hoy_colombia
      )

      # Campo para subir el documento escaneado con firmas
      archivo_subido = st.file_uploader(
          "Subir Acta Firmada (PDF, Imagen JPG/PNG)",
          type=["pdf", "png", "jpg", "jpeg"],
      )

      submit = st.form_submit_button("Guardar en el Sistema")

      if submit:
        file_name = ""
        mime_type = ""
        file_data_b64 = ""

        if archivo_subido is not None:
          file_name = archivo_subido.name
          mime_type = archivo_subido.type
          file_data_b64 = base64.b64encode(archivo_subido.getvalue()).decode(
              "utf-8"
          )

        datos_a_enviar = {
            "documento": str(nuevo_doc),
            "nombre": nuevo_nombre,
            "grado": nuevo_grado,
            "tipo_registro": tipo_reg,
            "detalles": detalles_reg,
            "fecha": str(fecha_reg),
            "fileName": file_name,
            "mimeType": mime_type,
            "fileData": file_data_b64,
        }

        try:
          # Enviar a Apps Script y capturar la respuesta con la URL generada
          response = requests.post(URL_APPS_SCRIPT, json=datos_a_enviar)
          res_json = response.json()
          url_generada = res_json.get("url", "Sin archivo")

          # Crear registro local con la URL correcta para que aparezca de inmediato
          nuevo_registro = {
              "documento": str(nuevo_doc),
              "nombre": nuevo_nombre,
              "grado": nuevo_grado,
              "tipo_registro": tipo_reg,
              "detalles": detalles_reg,
              "fecha": str(fecha_reg),
              "archivo": url_generada,
          }

          nuevo_df = pd.DataFrame([nuevo_registro])
          st.session_state.df = pd.concat(
              [st.session_state.df, nuevo_df], ignore_index=True
          )

          st.success(
              "¡Registro guardado y archivo subido a Google Drive con éxito!"
          )
          st.rerun()
        except Exception as e:
          st.error(f"Error al conectar con la base de datos en la nube: {e}")

    st.write("---")
    st.write("### Todos los Registros Institucionales")
    st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

  elif password:
    st.error("Contraseña incorrecta. Intente de nuevo.")
