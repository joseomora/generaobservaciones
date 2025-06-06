# app.py

import streamlit as st
import pandas as pd
import urllib.request
import json
import os

# --- Configuración de la Página ---
# Es bueno darle un título y un ícono a tu app.
st.set_page_config(
    page_title="Analizador de Texto con AI",
    page_icon="🤖",
    layout="centered"
)

# --- Función para Llamar a la API ---
# Movemos la lógica de la API a una función para mantener el código ordenado.
# La función toma el texto del usuario como entrada.
# Reemplaza la función completa con esta versión
def consumir_api_azure(texto_input: str):
    """
    Envía el texto a la API de Azure ML y devuelve los resultados.
    """
    # --- CAMBIO IMPORTANTE: LEEMOS DIRECTAMENTE DEL ENTORNO CON LA LIBRERÍA 'os' ---
    api_key = os.environ.get("API_KEY_AZURE")
    url = 'https://pruebacapacitacion-0621-xsxjf.eastus2.inference.ml.azure.com/score'

    # Verificamos si la variable de entorno fue encontrada
    if not api_key:
        st.error("La variable de entorno 'API_KEY_AZURE' no fue encontrada en la configuración de Azure.")
        # st.stop() detiene la ejecución del script aquí para no continuar con errores.
        st.stop()

    # El cuerpo (body) de la petición.
    data = {"resultados": texto_input}

    # Preparación de la petición
    body = str.encode(json.dumps(data))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ('Bearer ' + api_key),
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, body, headers)

    # Bloque try-except para manejar errores de la API
    try:
        response = urllib.request.urlopen(req)
        result_bytes = response.read()
        result_json_str = result_bytes.decode("utf8", 'ignore')
        result_list = json.loads(result_json_str)
        return result_list

    except urllib.error.HTTPError as error:
        error_message = f"La petición a la API falló con código {error.code}."
        error_details = error.read().decode("utf8", 'ignore')
        st.error(f"{error_message}\nDetalles: {error_details}")
        return None

# --- Interfaz de Usuario de Streamlit ---

st.title("🤖 Generador de Observaciones con IA")
st.markdown("Introduce un texto en el siguiente campo y presiona 'Generar Observación' para ver las propuestas.")

texto_usuario = st.text_area("Escribe aquí el texto que deseas analizar:", height=150)

if st.button("Generar Observación", type="primary"):
    if texto_usuario:
        with st.spinner('Conectando con la IA... por favor espera.'):
            resultados_api = consumir_api_azure(texto_usuario)

        if resultados_api:
            st.subheader("Resultados de la generación:")
            st.info("A continuación se muestran las 3 propuestas retornadas por el modelo.")

            try:
                lista_de_propuestas = resultados_api['propuestas']['propuestas']

                # --- LÓGICA DE TARJETAS CON MARKDOWN ---
                # Iteramos sobre cada propuesta y la mostramos en un bloque estilizado.
                for i, propuesta in enumerate(lista_de_propuestas):
                    st.markdown(f"**Propuesta {i+1}:**")
                    # Usamos un div de HTML para aplicar estilos directamente.
                    st.markdown(
                        f'<div style="font-size: 18px; text-align: justify; border-left: 4px solid #4A90E2; padding-left: 10px; margin-bottom: 20px;">'
                        f'{propuesta}'
                        '</div>',
                        unsafe_allow_html=True
                    )
                # -----------------------------------------

            except (KeyError, TypeError) as e:
                st.error(f"La estructura de datos de la API no es la esperada. Error: {e}")
                st.write("Datos recibidos de la API (para depuración):")
                st.json(resultados_api)

    else:
        st.warning("Por favor, introduce un texto para analizar.")

st.markdown("---")
st.write("Desarrollado por CDeIA usando Streamlit.")