import streamlit as st

def header_with_logo():
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #054750;'>🗺️ Pop Adjacent Area</h1>
            <p style='color: #666; font-size: 1.2em;'>Análise de Densidade Populacional com Buffers de Segurança</p>
            <hr style='border: 2px solid #054750;'>
        </div>
    """, unsafe_allow_html=True)

def sidebar_params(config):
    """Sidebar com todos os parâmetros configuráveis."""
    st.sidebar.markdown("### ⚙️ **Configurações**")
    
    # Buffers
    st.sidebar.subheader("📏 **Buffers (metros)**")
    buffers = {
        'fg_size': st.sidebar.number_input("Flight Geography", 
                                         value=config['buffers']['fg_size'], min_value=0.0),
        'cv_size': st.sidebar.number_input("Contingency Volume", 
                                         value=config['buffers']['cv_size'], min_value=0.0),
        'grb_size': st.sidebar.number_input("Ground Risk Buffer", 
                                          value=config['buffers']['grb_size'], min_value=0.0),
        'adj_size': st.sidebar.number_input("Adjacent Area", 
                                          value=config['buffers']['adj_size'], min_value=0.0)
    }
    
    # Grids IBGE
    st.sidebar.subheader("🗺️ **Grids IBGE**")
    urls = st.sidebar.multiselect(
        "Selecionar grids",
        options=config['ibge']['urls'],
        default=config['ibge']['default_urls']
    )
    
    return {'buffers': buffers, 'ibge': {'urls': urls}}
