import streamlit as st
from src.parameters import DEFAULT_PARAMS
from src.buffer_tool import generate_safety_margins_kml
from src.density_tool import calculate_density_plots
from src.report_generator import generate_pdf_report

st.set_page_config(page_title="Pop Adjacent Area v2.0", layout="wide")

# Sidebar com parâmetros do config
st.sidebar.header("⚙️ Configuração")
use_defaults = st.sidebar.checkbox("Usar padrões", True)
if not use_defaults:
    # Inputs customizados
    pass

# Multi-páginas automático
# Streamlit detecta ./pages/*.py automaticamente!

# Main page: workflow completo
if st.button("🚀 Executar Análise Completa"):
    # 1. Buffers → KML
    # 2. Densidade → Plots + Stats  
    # 3. Relatório PDF automático 👈
    with st.spinner("Gerando relatório completo..."):
        kml_bytes = generate_safety_margins_kml(...)
        plots, stats = calculate_density_plots(...)
        pdf_bytes = generate_pdf_report(..., plots, stats, ...)
    
    # Downloads múltiplos
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📄 Relatório PDF", pdf_bytes, "relatorio_completo.pdf")
    with col2: 
        st.download_button("🗺️ KML Buffers", kml_bytes, "safety_margins.kml")

