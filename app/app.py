import streamlit as st
import streamlit.components.v1 as components
import io
from src.buffer_tool import generate_safety_margins_kml
from src.density_tool import calculate_density_analysis
from src.report_generator import generate_pdf_report
from src.parameters import load_config
from app.utils.ui_components import sidebar_params, header_with_logo

st.set_page_config(
    page_title="Pop Adjacent Area v2.0", 
    page_icon="🗺️",
    layout="wide"
)

# CSS customizado
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração
config = load_config()

header_with_logo()

# Sidebar com parâmetros
params = sidebar_params(config)

# Upload principal
col1, col2 = st.columns([3, 1])
with col1:
    st.header("📁 Upload KML Original")
    kml_file = st.file_uploader("Escolha seu arquivo KML", type="kml")

with col2:
    st.info("**Parâmetros recomendados:**\n\n" +
            f"• FG: {params['buffers']['fg_size']}m\n" +
            f"• CV: {params['buffers']['cv_size']}m\n" +
            f"• GRB: {params['buffers']['grb_size']}m\n" +
            f"• ADJ: {params['buffers']['adj_size']}m")

if kml_file is not None:
    # Botão principal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **Executar Análise Completa**", type="primary", use_container_width=True):
            with st.spinner("🔄 Processando buffers → densidade → relatório..."):
                # 1. GERA BUFFERS
                kml_safety_bytes = generate_safety_margins_kml(
                    kml_file.read(), **params['buffers']
                )
                
                # 2. ANÁLISE DE DENSIDADE
                plots, stats = calculate_density_analysis(kml_safety_bytes, params['ibge']['urls'])
                
                # 3. RELATÓRIO PDF
                pdf_bytes = generate_pdf_report(
                    kml_file.name, kml_safety_bytes, plots, stats, params
                )
            
            # RESULTADOS
            st.success("✅ **Análise completa gerada!**")
            
            # Downloads
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "📄 Relatório PDF", 
                    pdf_bytes, 
                    f"relatorio_{kml_file.name.split('.')[0]}.pdf",
                    "application/pdf"
                )
            with col2:
                st.download_button(
                    "🗺️ KML com Buffers", 
                    kml_safety_bytes, 
                    f"safety_margins_{kml_file.name}"
                )
            with col3:
                st.download_button(
                    "📊 Dados Estatísticos", 
                    io.BytesIO(str(stats).encode()), 
                    "estatisticas.json"
                )
            
            # Preview dos mapas
            st.header("🗺️ **Mapas Gerados**")
            for i, fig in enumerate(plots):
                st.pyplot(fig)
