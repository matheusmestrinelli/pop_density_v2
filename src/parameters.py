import yaml
import os

def load_config(config_path="data/config.yaml"):
    """Carrega configuração ou usa defaults."""
    default_config = {
        'buffers': {
            'fg_size': 50.0,
            'cv_size': 100.0,
            'grb_size': 200.0,
            'adj_size': 500.0
        },
        'ibge': {
            'urls': [
                "https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/censo_2022/grade_estatistica/grade_id26.zip"
            ],
            'default_urls': [
                "https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/censo_2022/grade_estatistica/grade_id26.zip"
            ]
        }
    }
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            default_config.update(user_config)
    
    return default_config
