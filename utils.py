from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import qrcode
import io

def generar_comprobante_pdf(datos_usuario):
    buffer = io.BytesIO()

    # Crear PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Comprobante de Ticket de Turno")

    # Subtítulo y datos
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 90, f"Nombre: {datos_usuario['nombre']}")
    c.drawString(100, height - 110, f"CURP: {datos_usuario['curp']}")
    c.drawString(100, height - 130, f"Turno asignado: {datos_usuario['turno']}")
    c.drawString(100, height - 150, f"Municipio: {datos_usuario['municipio']}")
    c.drawString(100, height - 170, f"Asunto: {datos_usuario['asunto']}")

    # Generar QR con la CURP
    qr = qrcode.make(datos_usuario['curp'])
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Convertir BytesIO en un objeto compatible con reportlab
    qr_image = ImageReader(qr_io)

    # Insertar QR en el PDF
    c.drawImage(qr_image, 100, height - 350, width=150, height=150)

    # Finalizar PDF
    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer
