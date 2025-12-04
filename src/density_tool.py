import geopandas as gpd
import requests
import zipfile
import io
import os
import matplotlib.pyplot as plt
import contextily as cx
import tempfile
from matplotlib.lines import Line2D

ALBERS_BR = (
    "+proj=aea +lat_0=-12 +lon_0=-54 +lat_1=-2 +lat_2=-22 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)

COLORS = {
    'Flight Geography': 'green',
    'Contingency Volume': 'orange',
    'Ground Risk Buffer': 'red',
    'Adjacent Area': 'blue',
}

def extrair_layers_kml(kml_path: str):
    """Extrai layers do KML (SEU CÓDIGO EXATO)."""
    gdf = gpd.read_file(kml_path, driver='KML')
    layers_poligonos = {}
    layer_names = ["Flight Geography", "Contingency Volume", "Ground Risk Buffer", "Adjacent Area"]
    
    for name in layer_names:
        sel = gdf[gdf['Name'] == name]
        if sel.empty:
            continue
        sel = sel[sel.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        if sel.empty:
            continue
        layers_poligonos[name] = sel.geometry.union_all()
    return layers_poligonos

def carregar_grid_ibge(url):
    """Carrega grid IBGE (SEU CÓDIGO EXATO)."""
    grade_id = url.split('/')[-1].split('.')[0]
    pasta = f"data/ibge_cache/{grade_id}"
    shp_path = os.path.join(pasta, f"{grade_id}.shp")

    if not os.path.exists(shp_path):
        os.makedirs(pasta, exist_ok=True)
        resp = requests.get(url)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(pasta)

    return gpd.read_file(shp_path), grade_id

def calcular_estatisticas(dados_intersec):
    """Calcula estatísticas (SEU CÓDIGO EXATO)."""
    if dados_intersec.empty:
        return 0, 0.0, 0.0
    total_pessoas = float(dados_intersec['TOTAL'].sum())
    area_total_km2 = float((dados_intersec.geometry.area.sum()) / 1e6)
    densidade_media = (total_pessoas / area_total_km2) if area_total_km2 > 0 else 0.0
    return total_pessoas, area_total_km2, densidade_media

def plotar_mapa(url, area_geom, titulo, layers_poligonos, layers_para_mostrar):
    """Gera mapa de densidade (SEU CÓDIGO EXATO)."""
    grid, grade_id = carregar_grid_ibge(url)
    
    dados_filtrados = grid[grid.intersects(area_geom)].copy()
    if dados_filtrados.empty:
        return None

    dados_area = dados_filtrados.to_crs(ALBERS_BR)
    dados_area['area_km2'] = dados_area.geometry.area / 1e6
    dados_area['densidade_pop_km2'] = dados_area['TOTAL'] / dados_area['area_km2']
    dados_filtrados['densidade_pop_km2'] = dados_area['densidade_pop_km2'].values

    fig, ax = plt.subplots(figsize=(16, 12))
    dados_filtrados.plot(
        column='densidade_pop_km2', ax=ax, legend=True, cmap='YlOrBr',
        alpha=0.6, edgecolor='black', linewidth=0.2,
        legend_kwds={'shrink': 0.3, 'label': 'Densidade (hab/km²)'}
    )
    
    # Contornos
    for name in layers_para_mostrar:
        if name in layers_poligonos:
            gpd.GeoSeries([layers_poligonos[name]]).boundary.plot(
                ax=ax, color=COLORS[name], linewidth=2
            )
    
    ax.set_title(f"{titulo} ({grade_id})", fontsize=16)
    cx.add_basemap(ax, crs=dados_filtrados.crs.to_string(),
                  source=cx.providers.OpenStreetMap.Mapnik, alpha=0.6, zoom=13)
    
    total_pessoas, area_total_km2, densidade_media = calcular_estatisticas(dados_area)
    info_texto = (
        f"População: {int(total_pessoas):,}\n"
        f"Área: {area_total_km2:.2f} km²\n"
        f"Densidade: {densidade_media:.0f} hab/km²"
    )
    ax.text(0.02, 0.98, info_texto, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    return fig

def calculate_density_analysis(kml_content: bytes, urls: list):
    """Executa análise completa de densidade."""
    with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as temp_file:
        temp_file.write(kml_content)
        temp_path = temp_file.name
    
    try:
        layers_poligonos = extrair_layers_kml(temp_path)
        if not layers_poligonos:
            return [], {}
        
        plots = []
        stats = {}
        
        # PLOT 1: Flight Geography
        for url in urls:
            fig = plotar_mapa(url, layers_poligonos['Flight Geography'], 
                            "Densidade - Flight Geography", layers_poligonos, 
                            ['Flight Geography'])
            if fig:
                plots.append(fig)
        
        # PLOT 2: Ground Risk Buffer
        for url in urls:
            fig = plotar_mapa(url, layers_poligonos['Ground Risk Buffer'], 
                            "Densidade - Ground Risk Buffer", layers_poligonos, 
                            ['Flight Geography', 'Contingency Volume', 'Ground Risk Buffer'])
            if fig:
                plots.append(fig)
        
        # PLOT 3: Adjacent Area (anel)
        if 'Adjacent Area' in layers_poligonos and 'Contingency Volume' in layers_poligonos:
            for url in urls:
                area_anel = layers_poligonos['Adjacent Area'].difference(layers_poligonos['Contingency Volume'])
                fig = plotar_mapa(url, area_anel, "Densidade - Adjacent Area (Anel)", 
                                layers_poligonos, 
                                ['Flight Geography', 'Contingency Volume', 'Ground Risk Buffer', 'Adjacent Area'])
                if fig:
                    plots.append(fig)
        
        stats = {
            'total_plots': len(plots),
            'layers_found': list(layers_poligonos.keys())
        }
        
        return plots, stats
        
    finally:
        os.unlink(temp_path)

