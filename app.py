import streamlit as st
import pandas as pd
import requests
import json

# 1. Configuración de la página web
st.set_page_config(page_title="Asistente Corporativo Inteligente", page_icon="🤖", layout="centered")

# Configurar la API Key de Cohere desde los secretos seguros del servidor
if "COHERE_API_KEY" in st.secrets:
    cohere_key = st.secrets["COHERE_API_KEY"]
else:
    st.error("Falta la configuración de COHERE_API_KEY en los secretos del servidor.")
    st.stop()

# 2. Configuración de la base de datos (Google Sheets)
SHEET_ID = "1zCqf7ohMD2ouAfqMLoTBw8KuUozZGEHd"
MAP_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300) # Guarda en caché los datos por 5 minutos
def obtener_datos_contexto():
    try:
        df = pd.read_csv(MAP_URL)
        contexto_lista = []
        for index, row in df.iterrows():
            elementos_fila = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
            contexto_lista.append(" | ".join(elementos_fila))
        return "\n".join(contexto_lista)
    except Exception as e:
        return f"Error al cargar los datos del Excel: {str(e)}"

# 3. Interfaz Gráfica de Usuario (UI)
st.title("🤖 Asistente de IA Empresarial")
st.write("Pregúntame cualquier detalle sobre el inventario, políticas o datos internos de la empresa.")

# Inicializar historial de chat aislado por usuario
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar historial de conversación existente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Capturar consulta del usuario e interactuar con la IA
if user_query := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de datos..."):
            
            # Obtener la información del Excel actualizado
            datos_empresa = obtener_datos_contexto()
            
            # Diseñar el prompt del sistema instructivo (Inyectado en el preámbulo de Cohere)
            prompt_sistema = (
                "Eres el asistente virtual oficial de la empresa. Tu deber es responder preguntas de clientes o "
                "empleados basándote única y exclusivamente en los siguientes datos actuales extraídos de nuestro "
                "documento Excel interno:\n\n"
                f"{datos_empresa}\n\n"
                "Instrucciones estrictas:\n"
                "1. Si la información solicitada no está en los datos provistos, responde amablemente que no dispones "
                "de ese dato por el momento.\n"
                "2. Sé profesional, claro y conciso.\n"
                "3. Responde siempre en el mismo idioma en el que te hablan."
            )
            
            # --- CONEXIÓN DIRECTA CON COHERE API ---
            url = "https://api.cohere.com/v1/chat"
            
            headers = {
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            
            payload = {
                "message": user_query,
                "preamble": prompt_sistema,   # Contexto del Excel
                "model": "command-light"     # Modelo corporativo avanzado
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                if response.status_code == 200:
                    response_data = response.json()
                    output_text = response_data["text"]
                    
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                else:
                    st.error(f"Error de la API de Cohere (Código {response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Ocurrió un inconveniente al procesar la comunicación: {str(e)}")
