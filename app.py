# app.py

import streamlit as st
import pandas as pd
import urllib.request
import json
import os
import time

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

    /* FILA DE TARJETAS A ANCHO COMPLETO (Grid responsivo) */
    .proposal-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 20px;
        width: 100%;
        align-items: stretch;
        margin-top: 20px;
    }
    @media (max-width: 1200px){
        .proposal-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 800px){
        .proposal-row { grid-template-columns: 1fr; }
    }

    /* Tarjeta base: sin max-width para que ocupe el 100% de su celda */
    .proposal-card {
        width: 100%;
        height: 100%;
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .proposal-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .proposal-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .proposal-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .proposal-number {
        font-size: 14px;
        font-weight: bold;
        opacity: 0.9;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .proposal-content {
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
        overflow-wrap: anywhere; /* evita desbordes y asegura uso completo del ancho */
        word-break: break-word;
    }
    
    .icon-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
    }
    
    .input-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .stats-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .debug-container {
        background: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffc107;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Función para verificar el health check ---
def verificar_health_check():
    """
    Verifica si la API está disponible usando el endpoint /health
    """
    base_url = 'https://observaciones-api.nicebay-4b1a584e.eastus2.azurecontainerapps.io'
    health_url = f'{base_url}/health'
    
    try:
        req = urllib.request.Request(health_url)
        response = urllib.request.urlopen(req, timeout=5)
        if response.getcode() == 200:
            return True, "API disponible"
        return False, f"API respondió con código {response.getcode()}"
    except Exception as e:
        return False, str(e)

# --- Función para Llamar a la API ---
def consumir_api_azure(titulo: str, entidad: str, texto_input: str):
    """
    Envía el título, entidad y texto a la API de Azure y devuelve los resultados.
    """
    api_key = os.environ.get("API_KEY_AZURE")
    
    # URL base y endpoint correctos según el script de pruebas
    base_url = 'https://observaciones-api.nicebay-4b1a584e.eastus2.azurecontainerapps.io'
    endpoint = '/generate-observaciones'
    url = base_url + endpoint

    # Verificamos si la variable de entorno fue encontrada
    if not api_key:
        st.error("⚠️ La variable de entorno 'API_KEY_AZURE' no fue encontrada en la configuración.")
        st.info("💡 Asegúrate de configurar la variable en Streamlit Cloud: Settings > Secrets")
        return None

    # El cuerpo debe coincidir con el formato del script de pruebas
    # El script usa: resultados, titulo, entidad
    data = {
        "resultados": texto_input,  # Cambiado el orden para coincidir con el script
        "titulo": titulo,            # título sin tilde para evitar problemas de encoding
        "entidad": entidad
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
        # Aumentamos el timeout a 90 segundos como en el script de pruebas
        start_time = time.time()
        response = urllib.request.urlopen(req, timeout=90)
        elapsed_time = time.time() - start_time
        
        result_bytes = response.read()
        result_json_str = result_bytes.decode("utf8", 'ignore')
        result_json = json.loads(result_json_str)
        
        # Añadimos el tiempo de respuesta al resultado
        result_json['_response_time'] = elapsed_time
        
        return result_json

    except urllib.error.HTTPError as error:
        error_message = f"La petición a la API falló con código {error.code}."
        error_details = error.read().decode("utf8", 'ignore')
        st.error(f"❌ {error_message}")
        
        # Intentar parsear el error como JSON para más detalles
        try:
            error_json = json.loads(error_details)
            st.json(error_json)
        except:
            st.text(f"Detalles: {error_details}")
        
        return None
    
    except urllib.error.URLError as error:
        st.error(f"❌ Error de conexión: {error.reason}")
        st.info("💡 Verifica que la URL de la API sea correcta y esté accesible")
        return None
    
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return None

# --- Interfaz de Usuario de Streamlit ---

# Header principal con gradiente
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🎯 Generador de Observaciones con IA</h1>
    <p style="margin-top: 10px; opacity: 0.95;">Potenciado por Inteligencia Artificial para generar observaciones precisas y relevantes</p>
</div>
""", unsafe_allow_html=True)

# Sidebar con información de la API
with st.sidebar:
    st.markdown("### 🔧 Estado de la API")
    
    if st.button("🔄 Verificar Conexión"):
        with st.spinner("Verificando..."):
            is_healthy, message = verificar_health_check()
            if is_healthy:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
    
    st.markdown("---")
    st.markdown("### 📊 Información")
    st.info("""
    **Endpoint:** `/generate-observaciones`
    
    **Timeout:** 90 segundos
    
    **Formato esperado:**
    - resultados (texto)
    - titulo
    - entidad
    """)

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
        value=st.session_state.get('titulo_ejemplo', ''),
        placeholder="Ingrese el título del documento o proyecto",
        key="titulo_input",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 🏢 **Entidad**")
    entidad_usuario = st.text_input(
        "",
        value=st.session_state.get('entidad_ejemplo', ''),
        placeholder="Ingrese el nombre de la entidad u organización",
        key="entidad_input",
        label_visibility="collapsed"
    )

st.markdown("### 📄 **Texto para Analizar (Resultados)**")
texto_usuario = st.text_area(
    "",
    value=st.session_state.get('texto_ejemplo', ''),
    placeholder="Escriba o pegue aquí el texto que desea analizar para generar las observaciones...",
    height=200,
    key="texto_input",
    label_visibility="collapsed"
)

# Limpiar los valores de ejemplo después de usarlos
if 'titulo_ejemplo' in st.session_state:
    del st.session_state.titulo_ejemplo
if 'entidad_ejemplo' in st.session_state:
    del st.session_state.entidad_ejemplo
if 'texto_ejemplo' in st.session_state:
    del st.session_state.texto_ejemplo

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
        # Mostrar el payload que se enviará
        with st.expander("🔍 Ver payload a enviar", expanded=False):
            payload_preview = {
                "resultados": texto_usuario,
                "titulo": titulo_usuario,
                "entidad": entidad_usuario
            }
            st.json(payload_preview)
        
        with st.spinner('🔄 Conectando con la IA y generando observaciones... Este proceso puede tomar hasta 90 segundos.'):
            resultados_api = consumir_api_azure(titulo_usuario, entidad_usuario, texto_usuario)

        if resultados_api:
            st.markdown("---")
            st.markdown("""
            <h2 style="text-align: center; color: #333; margin-bottom: 30px;">
                ✨ Observaciones Generadas
            </h2>
            """, unsafe_allow_html=True)
            
            # Mostrar tiempo de respuesta si está disponible
            if '_response_time' in resultados_api:
                st.success(f"⏱️ Tiempo de respuesta: {resultados_api['_response_time']:.2f} segundos")
            
            # Mostrar información de contexto
            context_col1, context_col2 = st.columns(2)
            with context_col1:
                st.info(f"**📝 Título:** {titulo_usuario}")
            with context_col2:
                st.info(f"**🏢 Entidad:** {entidad_usuario}")

            try:
                # Ajustamos la estructura según lo que espera el script de pruebas
                propuestas = None
                
                # Opción 1: Array directo en 'propuestas'
                if 'propuestas' in resultados_api and isinstance(resultados_api['propuestas'], list):
                    propuestas = resultados_api['propuestas']
                
                # Opción 2: Estructura anidada
                elif 'propuestas' in resultados_api and isinstance(resultados_api['propuestas'], dict):
                    if 'propuestas' in resultados_api['propuestas']:
                        propuestas = resultados_api['propuestas']['propuestas']
                
                # Opción 3: Si la respuesta es directamente una lista
                elif isinstance(resultados_api, list):
                    propuestas = resultados_api
                
                if propuestas and len(propuestas) >= 3:
                    icons = ["🎯", "💡", "🔍"]
                    labels = ["ENFOQUE PRINCIPAL", "ALTERNATIVA 1", "ALTERNATIVA 2"]
                    card_classes = ["proposal-card-1", "proposal-card-2", "proposal-card-3"]

                    # Render a ancho completo en una grilla 3x
                    st.markdown('<div class="proposal-row">', unsafe_allow_html=True)
                    for i, propuesta in enumerate(propuestas[:3]):
                        propuesta_text = propuesta if isinstance(propuesta, str) else str(propuesta)
                        st.markdown(f"""
                        <div class="proposal-card {card_classes[i]}">
                            <div class="proposal-number">
                                <span>{icons[i]} PROPUESTA {i+1}</span>
                                <span class="icon-badge">{labels[i]}</span>
                            </div>
                            <div class="proposal-content">
                                {propuesta_text}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Sección de estadísticas
                    st.markdown("---")
                    st.markdown("### 📊 Estadísticas de las Observaciones")
                    
                    stat_cols = st.columns(3)
                    for i, propuesta in enumerate(propuestas[:3]):
                        propuesta_text = propuesta if isinstance(propuesta, str) else str(propuesta)
                        with stat_cols[i]:
                            palabras = len(propuesta_text.split())
                            caracteres = len(propuesta_text)
                            st.metric(
                                label=f"Propuesta {i+1}",
                                value=f"{palabras} palabras",
                                delta=f"{caracteres} caracteres"
                            )
                else:
                    st.error("❌ No se encontraron las 3 propuestas esperadas en la respuesta.")
                    with st.expander("🔍 Ver respuesta completa de la API", expanded=True):
                        st.json(resultados_api)

            except Exception as e:
                st.error(f"❌ Error al procesar la respuesta: {str(e)}")
                with st.expander("🔍 Ver datos recibidos (para depuración)", expanded=True):
                    st.json(resultados_api)
                    st.error(f"Tipo de respuesta: {type(resultados_api)}")
                    if isinstance(resultados_api, dict):
                        st.error(f"Claves disponibles: {list(resultados_api.keys())}")

# Footer mejorado
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 30px;">
    <p style="color: #666; margin: 0;">
        <strong>Desarrollado por CDeIA</strong> | Powered by Streamlit & Azure AI
    </p>
    <p style="color: #999; font-size: 0.9rem; margin-top: 5px;">
        🔒 Todos los datos son procesados de forma segura | Timeout: 90s
    </p>
</div>
""", unsafe_allow_html=True)
