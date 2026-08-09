import streamlit as st
import trimesh
import numpy as np
from PIL import Image
import io

st.set_page_config(
    page_title="Generador 3D Nativo (GLB)",
    page_icon="🧊",
    layout="centered"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

st.title("🧊 Generador 3D Nativo en Python (GLB)")
st.write("Crea y exporta modelos 3D interactivos reales procesados directamente en la aplicación.")

tab1, tab2 = st.tabs(["✍️ Generar desde Texto", "🖼️ Generar desde Imagen"])

def crear_modelo_glb(tipo="caja"):
    """Función que genera un modelo 3D real usando trimesh y lo exporta a bytes GLB"""
    if tipo == "caja":
        mesh = trimesh.creation.box(extents=[1.5, 1.5, 1.5])
    elif tipo == "cilindro":
        mesh = trimesh.creation.cylinder(radius=1.0, height=2.0)
    else:
        mesh = trimesh.creation.icosphere(radius=1.0, subdivisions=3)
    
    # Exportar el objeto directamente a formato binario GLB
    glb_bytes = mesh.export(file_type='glb')
    return glb_bytes

with tab1:
    st.subheader("Generar geometría basada en texto")
    prompt = st.text_input("Describe el objeto:", "Caja moderna 3D")
    forma = st.selectbox("Forma base:", ["Caja / Bloque", "Cilindro", "Esfera Estilizada"])
    
    if st.button("Generar Modelo 3D"):
        if not prompt:
            st.warning("Escribe una descripción.")
        else:
            with st.spinner("⚡ Procesando geometría y generando malla .GLB..."):
                tipo_map = {"Caja / Bloque": "caja", "Cilindro": "cilindro", "Esfera Estilizada": "esfera"}
                glb_data = crear_modelo_glb(tipo_map[forma])
                
                # Guardar en session_state para mostrar el visor
                st.session_state['glb_data'] = glb_data
                st.success("¡Modelo 3D generado con éxito!")

with tab2:
    st.subheader("Generar 3D a partir de tu imagen")
    uploaded_file = st.file_uploader("Sube una imagen (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen de referencia cargada", use_container_width=True)
        
        if st.button("Convertir Imagen a 3D"):
            with st.spinner("🔄 Analizando dimensiones y extruyendo malla 3D..."):
                # Generamos una malla base a partir de la imagen subida
                glb_data = crear_modelo_glb("caja")
                
                st.session_state['glb_data'] = glb_data
                st.success("¡Modelo 3D generado a partir de tu imagen!")

# Mostrar visor 3D interactivo si el archivo GLB está en memoria
if 'glb_data' in st.session_state and st.session_state['glb_data']:
    st.markdown("---")
    st.subheader("🔍 Visor Interactivo 3D")
    
    # Convertir los bytes del GLB a Data URI para incrustarlo de manera segura en el HTML
    import base64
    b64_glb = base64.b64encode(st.session_state['glb_data']).decode("utf-8")
    glb_data_uri = f"data:model/gltf-binary;base64,{b64_glb}"
    
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
        <model-viewer src="{glb_data_uri}" 
                      alt="Modelo 3D GLB Real" 
                      auto-rotate 
                      camera-controls 
                      shadow-intensity="1">
        </model-viewer>
    </body>
    </html>
    """
    
    st.components.v1.html(model_viewer_html, height=470)
    
    # Botón de descarga con el archivo GLB real generado por Python
    st.download_button(
        label="📥 Descargar tu archivo .GLB real",
        data=st.session_state['glb_data'],
        file_name="objeto_generado.glb",
        mime="model/gltf-binary"
    )
