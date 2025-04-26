from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import qrcode
import io

def generar_comprobante_pdf(datos_usuario):
    buffer = io.BytesIO()

    # Crear el PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Comprobante de Ticket de Turno")

    # Estilo
    c.setFont("Helvetica-Bold", 14)

    # Dibujar los datos
    c.drawString(1 * inch, height - 1 * inch, f"Nombre completo: {datos_usuario['nombre']}")
    c.drawString(1 * inch, height - 1.5 * inch, f"CURP: {datos_usuario['curp']}")
    c.drawString(1 * inch, height - 2 * inch, f"Turno: {datos_usuario['turno']}")
    c.drawString(1 * inch, height - 2.5 * inch, f"Teléfono: {datos_usuario['telefono']}")
    c.drawString(1 * inch, height - 3 * inch, f"Celular: {datos_usuario['celular']}")
    c.drawString(1 * inch, height - 3.5 * inch, f"Correo: {datos_usuario['correo']}")
    c.drawString(1 * inch, height - 4 * inch, f"Nivel: {datos_usuario['nivel']}")
    c.drawString(1 * inch, height - 4.5 * inch, f"Municipio: {datos_usuario['municipio']}")
    c.drawString(1 * inch, height - 5 * inch, f"Asunto: {datos_usuario['asunto']}")

    # 🧠 Crear el Código QR
    qr_data = datos_usuario['curp']
    qr = qrcode.make(qr_data)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    qr_image = ImageReader(qr_io)

    # Insertar QR
    c.drawImage(qr_image, 5.5 * inch, height - 3 * inch, width=2 * inch, height=2 * inch)

    # Finalizar PDF
    c.save()
    buffer.seek(0)

    return buffer