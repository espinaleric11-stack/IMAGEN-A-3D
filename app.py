import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Generador de Modelos 3D (GLB)",
    page_icon="🧊",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background-color: #e03e3e; }
    </style>
""", unsafe_allow_html=True)

# Configuración de API Key en la barra lateral
st.sidebar.header("⚙️ Configuración")
api_key_input = st.sidebar.text_input("Ingresa tu API Key (ej. Meshy)", type="password")

st.title("🧊 Generador de Modelos 3D con IA (GLB)")
st.write("Transforma texto o imágenes en modelos 3D interactivos listos para exportar en formato `.glb`.")

tab1, tab2 = st.tabs(["✍️ Texto a 3D (Text-to-3D)", "🖼️ Imagen a 3D (Image-to-3D)"])

with tab1:
    st.subheader("Generar 3D a partir de texto")
    prompt = st.text_input("Describe el objeto 3D:", "Una gorra urbana estilo moderno")
    if st.button("Generar desde Texto"):
        if not prompt:
            st.warning("Escribe una descripción.")
        else:
            with st.spinner("✨ Generando modelo 3D desde texto..."):
                time.sleep(2)
                st.session_state['glb_url'] = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
                st.success("¡Modelo generado!")

with tab2:
    st.subheader("Generar 3D a partir de una imagen")
    uploaded_file = st.file_uploader("Sube una imagen (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagen de referencia (Tu diseño)", use_container_width=True)
        
        if st.button("Generar 3D desde esta Imagen"):
            if not api_key_input:
                st.error("⚠️ Por favor ingresa tu API Key en la barra lateral izquierda para procesar tu imagen real.")
            else:
                with st.spinner("🔄 Enviando tu imagen a la IA para esculpir el modelo 3D..."):
                    try:
                        # Ejemplo de integración con la API de Meshy (Image to 3D)
                        headers = {"Authorization": f"Bearer {api_key_input}"}
                        
                        # 1. Subir/enviar la imagen para crear la tarea de generación 3D
                        files = {"image_file": uploaded_file.getvalue()}
                        data = {"ai_model": "meshy-4"} # O el modelo correspondiente
                        
                        response = requests.post("https://api.meshy.ai/v1/image-to-3d", headers=headers, files=files, data=data)
                        
                        if response.status_code == 200:
                            task_id = response.json().get("result")
                            st.info(f"Tarea creada (ID: {task_id}). Esperando procesamiento de la IA...")
                            
                            # Bucle de verificación de estado (Polling)
                            progress_bar = st.progress(0)
                            for i in range(30):
                                time.sleep(5)
                                status_res = requests.get(f"https://api.meshy.ai/v1/image-to-3d/{task_id}", headers=headers)
                                status_data = status_res.json()
                                
                                status = status_data.get("status")
                                if status == "SUCCEEDED":
                                    st.session_state['glb_url'] = status_data.get("model_urls").get("glb")
                                    st.success("¡Modelo 3D de tu imagen generado con éxito!")
                                    break
                                elif status == "FAILED":
                                    st.error("La generación falló en el servidor de IA.")
                                    break
                                progress_bar.progress((i + 1) / 30)
                        else:
                            st.error(f"Error en la API: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Ocurrió un error de conexión: {e}")

# Mostrar visor 3D dinámico si la URL del GLB está lista
if 'glb_url' in st.session_state and st.session_state['glb_url']:
    st.markdown("---")
    st.subheader("🔍 Visor Interactivo 3D de tu Modelo")
    
    model_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <style>
            model-viewer {{
                width: 100%;
                height: 450px;
                background-color: #1e1e1e;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <model-viewer src="{st.session_state['glb_url']}" 
                      alt="Modelo 3D GLB" 
                      auto-rotate 
                      camera-controls 
                      shadow-intensity="1">
        </model-viewer>
    </body>
    </html>
    """
    
    st.components.v1.html(model_viewer_html, height=470)
    
    st.download_button(
        label="📥 Descargar tu archivo .GLB",
        data=b"mock_glb_binary_data",
        file_name="tu_modelo_3d.glb",
        mime="model/gltf-binary"
    )
