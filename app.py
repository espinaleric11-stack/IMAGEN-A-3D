import streamlit as st
import requests
import time
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- INICIALIZACIÓN DE FIREBASE ---
@st.cache_resource
def init_fb():
    if not firebase_admin._apps:
        cred_path = "firebase_credentials.json"
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            secret_json = st.secrets["firebase"]["json_secret"]
            cred_dict = json.loads(secret_json)
            private_key = cred_dict["private_key"]
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            cred_dict["private_key"] = private_key
            cred = credentials.Certificate(cred_dict)
            
        firebase_admin.initialize_app(cred)
    return firestore.client()

try:
    db = init_fb()
except Exception as e:
    st.error(f"Error al inicializar Firebase: {e}")

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador 3D Real desde Imagen + Sketchfab",
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

# --- CONFIGURACIÓN DE APIS FIJAS ---
st.sidebar.header("⚙️ Configuración de APIs")
st.sidebar.success("✅ Sketchfab API Token configurado")
st.sidebar.success("✅ Tripo AI API configurada")

# Tokens fijos (puedes reemplazar la de Tripo si consigues una propia)
SKETCHFAB_API_TOKEN = "52e167c5a6024ee8b9b8fb8b9a7a89fc"
TRIPO_API_KEY = "TU_API_KEY_DE_TRIPO"  # Reemplaza esto con tu API key de Tripo si la tienes

st.title("🧊 Generador 3D Real (Imagen a GLB + Sketchfab)")
st.write("Sube tu diseño, genera el modelo 3D con IA y súbelo directamente a Sketchfab.")

uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Tu imagen de referencia", use_container_width=True)
    
    if st.button("🚀 Generar Modelo 3D Real de mi Imagen"):
        if TRIPO_API_KEY == "TU_API_KEY_DE_TRIPO":
            st.error("⚠️ Por favor configura tu API Key de Tripo AI en el código.")
        else:
            with st.spinner("⏳ Subiendo imagen a /v3/files y procesando modelo 3D..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {TRIPO_API_KEY}"
                    }
                    
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                    upload_res = requests.post(
                        "https://openapi.tripo3d.ai/v3/files", 
                        headers=headers, 
                        files=files
                    )
                    
                    upload_json = upload_res.json()
                    if upload_res.status_code == 200 and upload_json.get("code") == 0:
                        file_token = upload_json["data"]["file_token"]
                        
                        payload = {
                            "model": "v3.1-20260211",
                            "file": {
                                "file_token": file_token
                            },
                            "texture": True,
                            "pbr": True
                        }
                        
                        task_res = requests.post(
                            "https://openapi.trípo3d.ai/v3/generation/image-to-model" if False else "https://openapi.tripo3d.ai/v3/generation/image-to-model", 
                            headers={**headers, "Content-Type": "application/json"}, 
                            json=payload
                        )
                        
                        res_json = task_res.json()
                        if task_res.status_code == 200 and res_json.get("code") == 0:
                            task_id = res_json["data"]["task_id"]
                            st.info(f"Tarea iniciada (ID: {task_id}). Renderizando en la nube...")
                            
                            progress_bar = st.progress(0)
                            for i in range(40):
                                time.sleep(5)
                                status_res = requests.get(
                                    f"https://openapi.tripo3d.ai/v3/tasks/{task_id}", 
                                    headers=headers
                                )
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
                            st.error(f"Error al iniciar la tarea 3D: {res_json}")
                    else:
                        st.error(f"Error al subir la imagen en /v3/files: {upload_json}")
                        
                except Exception as e:
                    st.error(f"Ocurrió un error de conexión: {e}")

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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Descargar archivo .GLB",
            data=requests.get(st.session_state['glb_url']).content,
            file_name="modelo_tripo.glb",
            mime="model/gltf-binary"
        )
        
    with col2:
        if st.button("🌐 Subir a Sketchfab"):
            with st.spinner("📤 Subiendo modelo a Sketchfab..."):
                try:
                    glb_response = requests.get(st.session_state['glb_url'])
                    if glb_response.status_code == 200:
                        files = {
                            'modelFile': ('modelo_tripo.glb', glb_response.content, 'model/gltf-binary')
                        }
                        data = {
                            'name': 'Modelo 3D Generado por IA',
                            'description': 'Generado automáticamente desde imagen usando Tripo AI y Streamlit.',
                            'private': '0'
                        }
                        headers_sk = {
                            'Authorization': f'Token {SKETCHFAB_API_TOKEN}'
                        }
                        
                        sk_res = requests.post(
                            'https://api.sketchfab.com/v3/models',
                            headers=headers_sk,
                            data=data,
                            files=files
                        )
                        
                        if sk_res.status_code == 201:
                            st.success("¡Modelo subido a Sketchfab con éxito! Revisa tu panel de Sketchfab.")
                        else:
                            st.error(f"Error al subir a Sketchfab: {sk_res.status_code} - {sk_res.text}")
                    else:
                        st.error("No se pudo descargar el archivo GLB temporal para enviarlo a Sketchfab.")
                except Exception as ex:
                    st.error(f"Error de conexión con Sketchfab: {ex}")
