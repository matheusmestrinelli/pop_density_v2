import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import os
import tempfile

def generate_pdf_report(kml_name: str, kml_bytes: bytes, plots: list, stats: dict, params: dict) -> bytes:
    """Gera relatório PDF profissional."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Estilo customizado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Centralizado
    )
    
    story = []
    
    # CAPA
    story.append(Paragraph("RELATÓRIO DE ANÁLISE DE DENSIDADE POPULACIONAL", title_style))
    story.append(Paragraph(f"<b>Arquivo:</b> {kml_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Data:</b> {plt.datetime.date.today()}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # PARÂMETROS
    story.append(Paragraph("Parâmetros dos Buffers:", styles['Heading2']))
    params_text = (
        f"<bullet>• FG: {params['buffers']['fg_size']}m</bullet><br/>"
        f"<bullet>• CV: {params['buffers']['cv_size']}m</bullet><br/>"
        f"<bullet>• GRB: {params['buffers']['grb_size']}m</bullet><br/>"
        f"<bullet>• ADJ: {params['buffers']['adj_size']}m</bullet>"
    )
    story.append(Paragraph(params_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # MAPAS
    if plots:
        story.append(Paragraph("Mapas de Densidade:", styles['Heading2']))
        for i, fig in enumerate(plots[:3]):  # Máximo 3 mapas
            with tempfile.NamedTemporaryFile(suffix=f".png", delete=False) as tmp:
                fig.savefig(tmp.name, dpi=150, bbox_inches='tight')
                img = Image(tmp.name, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            os.unlink(tmp.name)
    
    # ESTATÍSTICAS
    story.append(Paragraph("Resumo Estatístico:", styles['Heading2']))
    stats_text = f"""
    <b>Layers analisados:</b> {', '.join(stats.get('layers_found', []))}<br/>
    <b>Total de mapas:</b> {stats.get('total_plots', 0)}
    """
    story.append(Paragraph(stats_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
