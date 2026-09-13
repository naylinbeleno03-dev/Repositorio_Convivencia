import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Repositorio Institucional - Convivencia", layout="centered"
)

st.title("Repositorio Digital de Convivencia Escolar")
st.write("Institución Educativa Técnica Sagrado Corazón")

# Cargar datos de forma segura
try:
  df = pd.read_csv("registros_convivencia.csv")
except FileNotFoundError:
  df = pd.DataFrame(
      columns=[
          "documento",
          "nombre",
          "grado",
          "tipo_registro",
          "detalles",
          "fecha",
      ]
  )

# 1. Selector de Rol inicial
rol = st.sidebar.selectbox(
    "Seleccione su perfil:",
    ["Estudiante", "Padre de Familia / Acudiente", "Docente / Directivo"],
)

st.markdown("---")

if rol == "Estudiante":
  st.subheader("Portal de Estudiante")
  doc_input = st.text_input(
      "Ingrese su Tarjeta de Identidad o Nombre completo:"
  )

  if doc_input:
    # Filtrar estrictamente por el documento o nombre del alumno
    resultado = df[
        df["documento"].astype(str).str.contains(doc_input, case=False, na=False)
        | df["nombre"].str.contains(doc_input, case=False, na=False)
    ]

    if not resultado.empty:
      st.success(
          "Registros encontrados (Visualización exclusiva de seguridad):"
      )
      for index, row in resultado.iterrows():
        st.info(
            f"**Fecha:** {row['fecha']} | **Tipo:**"
            f" {row['tipo_registro']}\n\n**Detalles:** {row['detalles']}"
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
            f"**Estudiante:** {row['nombre']} ({row['grado']})\n**Fecha:**"
            f" {row['fecha']} | **Tipo:** {row['tipo_registro']}\n**Detalles:**"
            f" {row['detalles']}"
        )
    else:
      st.warning("No se hallaron registros para el estudiante indicado.")

elif rol == "Docente / Directivo":
  st.subheader("Panel Administrativo")
  password = st.text_input("Ingrese la contraseña institucional:", type="password")

  # Contraseña de ejemplo (cámbiala por la que prefieras)
  if password == "Sagrado2026*":
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
      fecha_reg = st.date_input("Fecha")

      submit = st.form_submit_button("Guardar en el Sistema")

      if submit:
        nuevo_dato = pd.DataFrame(
            [{
                "documento": nuevo_doc,
                "nombre": nuevo_nombre,
                "grado": nuevo_grado,
                "tipo_registro": tipo_reg,
                "detalles": detalles_reg,
                "fecha": str(fecha_reg),
            }]
        )
        df = pd.concat([df, nuevo_dato], ignore_index=True)
        df.to_csv("registros_convivencia.csv", index=False)
        st.success("¡Registro guardado exitosamente en el archivo CSV!")

    st.write("---")
    st.write("### Todos los Registros Institucionales")
    st.dataframe(df)

  elif password:
    st.error("Contraseña incorrecta. Intente de nuevo.")