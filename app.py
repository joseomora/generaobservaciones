# app.py

import streamlit as st
import pandas as pd
import urllib.request
import json
import os

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Generador de Observaciones con IA",
    page_icon="🎯",
    layout="wide"
)

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
    
    .proposal-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .proposal-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .proposal-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .proposal-number {
        font-size: 14px;
        font-weight: bold;
        opacity: 0.9;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    
    .proposal-content {
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
    }
    
    .icon-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 5px 10px;
        border-radius: 20px;
        margin-left: 10px;
        font-size: 12px;
    }
    
    .input-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Función para Llamar a la API ---
def consumir_api_azure(titulo: str, entidad: str, texto_input: str):
    """
    Envía el título, entidad y texto a la API de Azure y devuelve los resultados.
    """
    api_key = os.environ.get("API_KEY_AZURE")
    # URL actualizada
    url = 'https://observaciones-api.nicebay-4b1a584e.eastus2.azurecontainerapps.io'

    # Verificamos si la variable de entorno fue encontrada
    if not api_key:
        st.error("⚠️ La variable de entorno 'API_KEY_AZURE' no fue encontrada en la configuración.")
        st.stop()

    # El cuerpo actualizado con los tres campos
    data = {
        "título": titulo,
        "entidad": entidad,
        "resultados": texto_input
    }

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
        st.error(f"❌ {error_message}\nDetalles: {error_details}")
        return None

# --- Interfaz de Usuario de Streamlit ---

# Header principal con gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🎯 Generador de Observaciones con IA</h1>
    <p style="margin-top: 10px; opacity: 0.95;">Potenciado por Inteligencia Artificial para generar observaciones precisas y relevantes</p>
</div>
""", unsafe_allow_html=True)

# Descripción
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <p style="font-size: 1.1rem; color: #666;">
        Complete los campos a continuación para generar tres propuestas de observaciones personalizadas.
    </p>
</div>
""", unsafe_allow_html=True)

# Sección de inputs con mejor diseño
st.markdown('<div class="input-section">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 **Título**")
    titulo_usuario = st.text_input(
        "",
        placeholder="Ingrese el título del documento o proyecto",
        key="titulo_input",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 🏢 **Entidad**")
    entidad_usuario = st.text_input(
        "",
        placeholder="Ingrese el nombre de la entidad u organización",
        key="entidad_input",
        label_visibility="collapsed"
    )

st.markdown("### 📄 **Texto para Analizar**")
texto_usuario = st.text_area(
    "",
    placeholder="Escriba o pegue aquí el texto que desea analizar para generar las observaciones...",
    height=200,
    key="texto_input",
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

# Botón centrado y mejorado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generar_button = st.button(
        "🚀 Generar Observaciones",
        type="primary",
        use_container_width=True
    )

if generar_button:
    # Validación de campos
    if not titulo_usuario:
        st.warning("⚠️ Por favor, ingrese un título.")
    elif not entidad_usuario:
        st.warning("⚠️ Por favor, ingrese una entidad.")
    elif not texto_usuario:
        st.warning("⚠️ Por favor, ingrese el texto a analizar.")
    else:
        with st.spinner('🔄 Conectando con la IA y generando observaciones... por favor espera.'):
            resultados_api = consumir_api_azure(titulo_usuario, entidad_usuario, texto_usuario)

        if resultados_api:
            st.markdown("---")
            st.markdown("""
            <h2 style="text-align: center; color: #333; margin-bottom: 30px;">
                ✨ Observaciones Generadas
            </h2>
            """, unsafe_allow_html=True)
            
            # Mostrar información de contexto
            context_col1, context_col2 = st.columns(2)
            with context_col1:
                st.info(f"**📝 Título:** {titulo_usuario}")
            with context_col2:
                st.info(f"**🏢 Entidad:** {entidad_usuario}")

            try:
                lista_de_propuestas = resultados_api['propuestas']['propuestas']

                # Crear tres columnas para las propuestas
                cols = st.columns(3)
                
                # Iconos y etiquetas diferentes para cada propuesta
                icons = ["🎯", "💡", "🔍"]
                labels = ["ENFOQUE PRINCIPAL", "ALTERNATIVA INNOVADORA", "PERSPECTIVA COMPLEMENTARIA"]
                card_classes = ["proposal-card-1", "proposal-card-2", "proposal-card-3"]
                
                for i, (col, propuesta) in enumerate(zip(cols, lista_de_propuestas)):
                    with col:
                        st.markdown(f"""
                        <div class="{card_classes[i]}">
                            <div class="proposal-number">
                                <span>{icons[i]} PROPUESTA {i+1}</span>
                                <span class="icon-badge">{labels[i]}</span>
                            </div>
                            <div class="proposal-content">
                                {propuesta}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Sección de estadísticas
                st.markdown("---")
                st.markdown("### 📊 Estadísticas de las Observaciones")
                
                stat_cols = st.columns(3)
                for i, propuesta in enumerate(lista_de_propuestas):
                    with stat_cols[i]:
                        palabras = len(propuesta.split())
                        caracteres = len(propuesta)
                        st.metric(
                            label=f"Propuesta {i+1}",
                            value=f"{palabras} palabras",
                            delta=f"{caracteres} caracteres"
                        )

            except (KeyError, TypeError) as e:
                st.error(f"❌ La estructura de datos de la API no es la esperada. Error: {e}")
                with st.expander("🔍 Ver datos recibidos (para depuración)"):
                    st.json(resultados_api)

# Footer mejorado
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 30px;">
    <p style="color: #666; margin: 0;">
        <strong>Desarrollado por CDeIA</strong> | Powered by Streamlit & Azure AI
    </p>
    <p style="color: #999; font-size: 0.9rem; margin-top: 5px;">
        🔒 Todos los datos son procesados de forma segura
    </p>
</div>
""", unsafe_allow_html=True)