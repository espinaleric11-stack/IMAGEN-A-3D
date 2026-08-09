import streamlit as st
import requests
import time
import base64

st.set_page_config(
    page_title="Generador 3D Real desde Imagen",
    page_icon="🧊",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #0284c7;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background-color: #0369a1; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Configuración de API")
api_key = st.sidebar.text_input("API Key de Tripo AI", type="password")

st.title("🧊 Generador 3D Real (Imagen a GLB)")
st.write("Sube tu diseño y la IA generará el modelo 3D volumétrico real.")

uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Tu imagen de referencia", use_container_width=True)
    
    if st.button("🚀 Generar Modelo 3D Real de mi Imagen"):
        if not api_key:
            st.error("⚠️ Por favor introduce tu API Key de Tripo en la barra lateral izquierda.")
        else:
            with st.spinner("⏳ Procesando imagen y conectando con la API v3 de Tripo..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Convertir la imagen a base64 para enviarla en el JSON de la API v3
                    encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    ext = uploaded_file.name.split('.')[-1].lower()
                    if ext == 'jpg':
                        ext = 'jpeg'
                        
                    payload = {
                        "type": "image_to_model",
                        "file": {
                            "type": ext,
                            "data": encoded_image
                        }
                    }
                    
                    # Usar el endpoint oficial v3
                    task_res = requests.post("https://openapi.tripo3d.ai/v3/openapi/task", headers=headers, json=payload)
                    
                    if task_res.status_code == 200 and task_res.json().get("code") == 0:
                        task_id = task_res.json()["data"]["task_id"]
                        st.info(f"Tarea creada con éxito (ID: {task_id}). Renderizando en la nube...")
                        
                        # Monitorear el progreso de la tarea (Polling)
                        progress_bar = st.progress(0)
                        for i in range(40):
                            time.sleep(5)
                            status_res = requests.get(f"https://openapi.tripo3d.ai/v3/openapi/task/{task_id}", headers={"Authorization": f"Bearer {api_key}"})
                            status_data = status_res.json()
                            
                            if status_data.get("code") == 0:
                                task_info = status_data["data"]
                                progress = task_info.get("progress", 0)
                                progress_bar.progress(progress / 100)
                                
                                if task_info.get("status") == "success":
                                    glb_result_url = task_info["output"]["model"]
                                    st.session_state['glb_url'] = glb_result_url
                                    st.success("¡Modelo 3D generado con éxito!")
                                    st.rerun()
                                    break
                                elif task_info.get("status") == "failed":
                                    st.error("La IA indicó que falló la conversión del modelo.")
                                    break
                    else:
                        st.error(f"Error de la API: {task_res.text}")
                        
                except Exception as e:
                    st.error(f"Ocurrió un error de conexión: {e}")

# Mostrar visor 3D en cuanto la URL del GLB esté lista
if 'glb_url' in st.session_state and st.session_state['glb_url']:
    st.markdown("---")
    st.subheader("🔍 Visor 3D de tu Diseño")
    
    model_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <style>
            model-viewer {{
                width: 100%;
                height: 450px;
                background-color: #111827;
                border-radius: 12px;
            }}
        </style>
    </head>
    <body>
        <model-viewer src="{st.session_state['glb_url']}" 
                      alt="Modelo 3D Generado" 
                      auto-rotate 
                      camera-controls>
        </model-viewer>
    </body>
    </html>
    """
    st.components.v1.html(model_viewer_html, height=470)
    
    st.download_button(
        label="📥 Descargar tu archivo .GLB",
        data=requests.get(st.session_state['glb_url']).content,
        file_name="modelo_tripo.glb",
        mime="model/gltf-binary"
    )
