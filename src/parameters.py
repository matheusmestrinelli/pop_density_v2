# Parâmetros configuráveis e padrões
DEFAULT_PARAMS = {
    "buffers": {
        "fg_size": 50.0,
        "cv_size": 100.0, 
        "grb_size": 200.0,
        "adj_size": 500.0
    },
    "ibge": {
        "urls": [
            "https://geoftp.ibge.gov.br/.../grade_id26.zip"
        ],
        "cache_dir": "data/ibge_cache/"
    },
    "map": {
        "zoom": 13,
        "cmap": "YlOrBr",
        "basemap": "OpenStreetMap.Mapnik"
    },
    "report": {
        "include_plots": True,
        "format": "pdf"
    }
}

def load_params(config_path="data/config.yaml"):
    """Carrega parâmetros de YAML ou usa defaults."""
    # Implementação flexível para expansão
    pass
