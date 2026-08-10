import streamlit as st
import requests
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
    page_title="Subidor Directo a Sketchfab",
    page_icon="🌐",
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

# --- CONFIGURACIÓN DE SKETCHFAB ---
SKETCHFAB_API_TOKEN = "52e167c5a6024ee8b9b8fb8b9a7a89fc"

st.sidebar.header("⚙️ Configuración")
st.sidebar.success("✅ Sketchfab API Token configurado")

st.title("🌐 Subidor de Modelos 3D a Sketchfab")
st.write("Sube tu archivo de modelo 3D (GLB o ZIP con OBJ) y publícalo directamente en tu cuenta de Sketchfab.")

uploaded_model = st.file_uploader("Sube tu modelo 3D", type=["glb", "gltf", "zip"])

model_name = st.text_input("Título del modelo", "Mi Modelo 3D")
model_description = st.text_area("Descripción", "Subido automáticamente desde mi app de Streamlit.")
is_private = st.checkbox("¿Modelo privado?", value=False)

if uploaded_model is not None:
    # Mostrar visor si es formato GLB
    if uploaded_model.name.endswith(".glb"):
        st.markdown("### 🔍 Vista Previa")
        # Guardar temporalmente en bytes para el visor
        model_bytes = uploaded_model.getvalue()
        
        # Generar URL de datos local para el visor
        import base64
        b64_encoded = base64.b64encode(model_bytes).decode("utf-8")
        data_url = f"data:model/gltf-binary;base64,{b64_encoded}"
        
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
            <model-viewer src="{data_url}" 
                        alt="Modelo 3D" 
                        auto-rotate 
                        camera-controls>
            </model-viewer>
        </body>
        </html>
        """
        st.components.v1.html(model_viewer_html, height=470)

    if st.button("🚀 Publicar en Sketchfab"):
        with st.spinner("📤 Subiendo modelo a Sketchfab..."):
            try:
                files = {
                    'modelFile': (uploaded_model.name, uploaded_model.getvalue(), uploaded_model.type)
                }
                data = {
                    'name': model_name,
                    'description': model_description,
                    'private': '1' if is_private else '0'
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
                    result_data = sk_res.json()
                    st.success("¡Modelo subido a Sketchfab con éxito! Revisa tu panel de Sketchfab.")
                    if 'uid' in result_data:
                        st.markdown(f"🔗 **Enlace del modelo:** https://sketchfab.com/models/{result_data['uid']}")
                else:
                    st.error(f"Error al subir a Sketchfab: {sk_res.status_code} - {sk_res.text}")
                    
            except Exception as ex:
                st.error(f"Error de conexión con Sketchfab: {ex}")
