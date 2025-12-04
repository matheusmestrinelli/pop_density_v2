import simplekml
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import io
import os
import tempfile

def generate_safety_margins_kml(kml_content: bytes, fg_size: float, cv_size: float, 
                               grb_size: float, adj_size: float) -> bytes:
    """Gera KML com 4 layers de buffers. Retorna bytes do KML."""
    
    # Salva temporariamente
    with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as temp_file:
        temp_file.write(kml_content)
        temp_path = temp_file.name
    
    try:
        # LÊ KML ORIGINAL (SEU CÓDIGO EXATO)
        gdf = gpd.read_file(temp_path)
        gdf = gdf.to_crs(epsg=31983)
        
        # Detecta polígonos
        has_polygon = any(gdf.geometry.type.isin(['Polygon', 'MultiPolygon']))
        
        # Cria cópias para cada layer
        gdf_fg = gdf.copy()
        gdf_cv = gdf.copy()
        gdf_grb = gdf.copy()
        gdf_adj = gdf.copy()
        
        # FG buffer (só se não for polígono)
        if not has_polygon:
            gdf_fg["geometry"] = gdf_fg.geometry.buffer(fg_size, cap_style=3)
        
        # Buffers cumulativos
        gdf_cv["geometry"] = gdf_cv.geometry.buffer(cv_size + fg_size, cap_style=3)
        gdf_grb["geometry"] = gdf_grb.geometry.buffer(grb_size + cv_size + fg_size, cap_style=3)
        gdf_adj["geometry"] = gdf_adj.geometry.buffer(adj_size + cv_size + fg_size, cap_style=3)
        
        # Converte para WGS84
        for layer in [gdf_fg, gdf_cv, gdf_grb, gdf_adj]:
            layer.to_crs(epsg=4326, inplace=True)
        
        # CORES KML (SEU CÓDIGO EXATO)
        colors = {
            'Flight Geography': {'fill': '3300ff00', 'outline': 'ff00ff00', 'width': 2},
            'Contingency Volume': {'fill': '1a00ffff', 'outline': 'ff00ffff', 'width': 2},
            'Ground Risk Buffer': {'fill': '1a0000ff', 'outline': 'ff0000ff', 'width': 2},
            'Adjacent Area': {'fill': '00ff0000', 'outline': 'ffff0000', 'width': 1},
        }
        
        # CRIA KML (SEU CÓDIGO EXATO)
        kml = simplekml.Kml()
        folder = kml.newfolder(name="Safety Margins")
        
        layers = [
            ('Flight Geography', gdf_fg),
            ('Contingency Volume', gdf_cv),
            ('Ground Risk Buffer', gdf_grb),
            ('Adjacent Area', gdf_adj)
        ]
        
        for name, layer in layers:
            for index, row in layer.iterrows():
                geom = row['geometry']
                if isinstance(geom, Polygon):
                    polygons = [geom]
                elif isinstance(geom, MultiPolygon):
                    polygons = geom.geoms
                else:
                    polygons = [geom.buffer(0, cap_style=2)]
                
                for poly in polygons:
                    if isinstance(poly, Polygon):
                        coords = [(x, y) for x, y in zip(*poly.exterior.coords.xy)]
                        pol = folder.newpolygon(name=name, outerboundaryis=coords)
                        pol.style.polystyle.color = colors[name]['fill']
                        pol.style.polystyle.fill = 1
                        pol.style.linestyle.color = colors[name]['outline']
                        pol.style.linestyle.width = colors[name]['width']
        
        # Retorna bytes
        output_bytes = io.BytesIO()
        kml.save(output_bytes)
        return output_bytes.getvalue()
        
    finally:
        os.unlink(temp_path)
