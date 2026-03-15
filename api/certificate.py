from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_certificate(company, project, credits, tx_hash, filename):

    c = canvas.Canvas(filename, pagesize=letter)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, 700, "Blue Carbon Offset Certificate")

    c.setFont("Helvetica", 12)

    c.drawString(100, 650, f"Company: {company}")
    c.drawString(100, 620, f"Project: {project}")
    c.drawString(100, 590, f"Carbon Credits: {credits} tCO2e")
    c.drawString(100, 560, f"Blockchain TX: {tx_hash}")

    c.drawString(100, 520, "Issued by: Blue Carbon Registry")

    c.save()