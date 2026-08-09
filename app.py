import streamlit as st
import time

st.set_page_config(
    page_title="Generador de Modelos 3D (GLB)",
    page_icon="🧊",
    layout="centered"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #e03e3e;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧊 Generador de Modelos 3D con IA (GLB)")
st.write("Transforma texto o imágenes en modelos 3D interactivos listos para exportar en formato `.glb`.")

# Pestañas de entrada
tab1, tab2 = st.tabs(["✍️ Texto a 3D (Text-to-3D)", "🖼️ Imagen a 3D (Image-to-3D)"])

with tab1:
    st.subheader("Generar 3D a partir de texto")
    prompt = st.text_input("Describe el objeto 3D que deseas crear:", "Un cofre de madera antiguo estilo cartoon, texturizado")
    art_style = st.selectbox("Estilo artístico:", ["Realista", "Cartoon / Low Poly", "Sci-Fi", "Fantasía"])
    
    if st.button("Generar desde Texto"):
        if not prompt:
            st.warning("Por favor ingresa una descripción.")
        else:
            with st.spinner("✨ La IA está esculpiendo y texturizando tu modelo 3D... (Esto puede tomar unos segundos)"):
                time.sleep(3) # Simulación de llamada a API de IA (ej: Meshy / Tripo)
                st.session_state['glb_url'] = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
                st.success("¡Modelo 3D generado con éxito!")

with tab2:
    st.subheader("Generar 3D a partir de una imagen")
    uploaded_file = st.file_uploader("Sube una imagen (PNG, JPG)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagen de referencia", use_column_width=True)
        if st.button("Generar desde Imagen"):
            with st.spinner("🔄 Analizando la geometría de la imagen y generando malla 3D..."):
                time.sleep(3)
                st.session_state['glb_url'] = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
                st.success("¡Modelo 3D generado con éxito desde tu imagen!")

# Mostrar visor 3D si hay un modelo disponible
if 'glb_url' in st.session_state and st.session_state['glb_url']:
    st.markdown("---")
    st.subheader("🔍 Visor Interactivo 3D")
    st.info("Puedes rotar, hacer zoom y mover el modelo con el ratón.")
    
    # Componente HTML con Google Model Viewer para incrustar el GLB en Streamlit
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
    
    # Botón de descarga
    st.download_button(
        label="📥 Descargar archivo .GLB",
        data=b"mock_glb_binary_data", # En producción real aquí cargas los bytes del archivo .glb descargado de la API
        file_name="modelo_3d_ia.glb",
        mime="model/gltf-binary"
    )
