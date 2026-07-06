# Capturar consulta del usuario (Alineado completamente a la izquierda)
if user_query := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generar respuesta de la IA (4 espacios de sangría)
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la base de datos..."):
            
            # 1. Obtener la información del Excel actualizado (12 espacios de sangría)
            datos_empresa = obtener_datos_contexto()
            
            # 2. Diseñar el prompt del sistema instructivo
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
            
            # --- CONEXIÓN DIRECTA POR HTTP (OPCIÓN 3) ---
            import requests
            import json

            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{prompt_sistema}\n\nPregunta del usuario: {user_query}"}
                        ]
                    }
                ]
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    response_data = response.json()
                    output_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                else:
                    st.error(f"Error de la API de Google (Código {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Ocurrió un inconveniente al procesar la comunicación directa: {str(e)}")
                
