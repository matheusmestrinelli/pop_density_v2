import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.plt import PDFDocument

def generate_pdf_report(kml_path: str, plots: list, stats: dict, output_path: str):
    """Gera relatório PDF automático com mapas + estatísticas."""
    # Capa + plots + tabela de densidades + KML link
    doc = PDFDocument(output_path)
    doc.add_page()
    
    # Adiciona cada plot como imagem
    for i, fig in enumerate(plots):
        fig.savefig(f"temp_plot_{i}.png")
        doc.add_image(f"temp_plot_{i}.png", ...)
    
    # Estatísticas em tabela
    doc.add_table(stats)
    doc.save()
