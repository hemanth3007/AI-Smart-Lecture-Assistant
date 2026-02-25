import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_pdf(filename, transcript, summary, score):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    elements.append(Paragraph("<b>Transcript:</b>", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(transcript, normal_style))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("<b>Summary:</b>", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(summary, normal_style))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"<b>Quiz Score:</b> {score}/5", normal_style))

    doc.build(elements)