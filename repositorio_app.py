import base64
from datetime import date, datetime
import os
import pandas as pd
import requests
import streamlit as st
from zoneinfo import ZoneInfo

# Intentar importar python-docx para procesar archivos .docx subidos
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# Configuración de la página
st.set_page_config(
    page_title="Repositorio Institucional - Convivencia", layout="centered"
)

# Estilos CSS optimizados con máxima visibilidad en modo claro y oscuro
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
    }
    
    /* Barra lateral en azul oscuro elegante */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }

    /* Estilo para el expander en la barra lateral */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: #334155 !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] details {
        background-color: #334155 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {
        color: #FDE047 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] p,
    section[data-testid="stSidebar"] div[data-testid="stExpander"] li {
        color: #F1F5F9 !important;
        font-size: 0.9rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stExpander"] a {
        color: #FDE047 !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
    }

    .header-box {
        background-color: #0F172A !important;
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
        color: #FFFFFF !important;
        margin-top: 6px !important;
        margin-bottom: 0 !important;
        font-size: 0.95rem !important;
    }

    /* CORRECCIÓN DE BOTONES PARA MODO OSCURO Y CLARO: FORZAR LEGIBILIDAD DEL TEXTO */
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    .stButton > button, 
    div[data-testid="stDownloadButton"] > button, 
    .stFormSubmitButton > button, 
    a[data-testid="stLinkButton"] {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
    }

    /* Forzar texto e íconos en blanco */
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="baseButton-primary"] *,
    .stButton > button *, 
    div[data-testid="stDownloadButton"] > button *, 
    .stFormSubmitButton > button *, 
    a[data-testid="stLinkButton"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Estado Hover (al pasar el cursor) */
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button:hover, 
    div[data-testid="stDownloadButton"] > button:hover, 
    .stFormSubmitButton > button:hover, 
    a[data-testid="stLinkButton"]:hover {
        background-color: #D4AF37 !important;
        color: #0F172A !important;
        border-color: #D4AF37 !important;
    }

    button[data-testid="baseButton-secondary"]:hover *,
    button[data-testid="baseButton-primary"]:hover *,
    .stButton > button:hover *, 
    div[data-testid="stDownloadButton"] > button:hover *, 
    .stFormSubmitButton > button:hover *, 
    a[data-testid="stLinkButton"]:hover * {
        color: #0F172A !important;
        fill: #0F172A !important;
    }

    [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
        color: #1F2937 !important;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

    hr {
        border-color: #64748B !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado superior
st.markdown(
    """
    <div class="header-box">
        <h1>Repositorio Digital de Convivencia Escolar</h1>
        <p>Institución Educativa Técnica Sagrado Corazón.</p>
    </div>
""",
    unsafe_allow_html=True,
)

SHEET_ID = "1eUTG3EFoVvRDpycgNv6JdUP_jAa4106SCCNhXIQGFsc"
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbyXVhL0eaD_ZYAMQxPMlzYOKIxHEy3OfTHVI7k6iv8Izcns7HYRtfS81zbDohwv2yZL/exec"

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

st.sidebar.header("Panel de Control")
rol = st.sidebar.selectbox(
    "Seleccione su perfil:",
    ["Padre de Familia / Acudiente", "Docente / Directivo"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Asistente Virtual")
st.sidebar.markdown(
    "[Abrir Chatbot de"
    " Convivencia](https://chatbot-convivencia-sena-edehd4uhj9lkziarpaexb2.streamlit.app/)"
)


def limpiar_texto_detalles(texto):
    if not texto or str(texto).strip().lower()
