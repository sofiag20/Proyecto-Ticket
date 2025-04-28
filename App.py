from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file
import requests
from datetime import datetime
from fpdf import FPDF
import qrcode
import io
from io import BytesIO
from utils import generar_comprobante_pdf
from flask import jsonify
from models.CRUD import valida_admin
from models.Database import Database
from models import db 



app = Flask(__name__)

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Ruta de bienvenida
@app.route('/')
def bienvenida():
    return render_template('Bienvenidos.html') 

# Ruta de login para administrador
@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        captcha_response = request.form.get('g-recaptcha-response')

        print("Usuario:", username)
        print("Contraseña:", password)
        print("Captcha Response:", captcha_response)

        if not captcha_response:
            flash('Por favor marca el captcha.')
            return redirect(url_for('login_admin'))

        secret_key = '6LcRFR4rAAAAAI9KutdEsPK7FoFI0MmPKRXTpiPC'
        payload = {'secret': secret_key, 'response': captcha_response}
        result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()
        print("Captcha resultado:", result)

        if not result.get('success'):
            flash('Captcha inválido.')
            return redirect(url_for('login_admin'))

        if valida_admin(username, password):
            print("Login exitoso")
            session['admin'] = username
            return redirect(url_for('admin_panel'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login_admin'))

    return render_template('login-admin.html')


@app.route('/index')
def index():
    db = Database()
    
    db.cursor.execute("SELECT cve_nivel, nivel FROM niveles ORDER BY nivel")
    niveles = db.cursor.fetchall()

    db.cursor.execute("SELECT cve_mun, nombre_mun FROM municipios ORDER BY nombre_mun")
    municipios = db.cursor.fetchall()

    db.cursor.execute("SELECT id_asunto, asunto FROM asuntos ORDER BY asunto")
    asuntos = db.cursor.fetchall()

    return render_template('index.html', niveles=niveles, municipios=municipios, asuntos=asuntos)


# Ruta del panel de administración
@app.route('/admin-panel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))  
    return render_template('admin-panel.html')  


@app.route('/logout')
def logout():
    session.pop('admin', None)  
    return redirect(url_for('bienvenida')) 


@app.route('/registrar-turno', methods=['POST'])
def registrar_turno():
    try:
        nombre_completo = request.form['nombre_completo']
        curp = request.form['curp']
        nombres = request.form['nombres'].title()
        paterno = request.form['paterno'].title()
        materno = request.form['materno'].title()
        telefono = request.form['telefono']
        celular = request.form['celular']
        correo = request.form['correo']
        nivel_id = int(request.form['nivel'])
        municipio_id = int(request.form['municipio'])
        asunto_id = int(request.form['id_asunto'])
    except Exception as e:
        flash(f"Error al obtener datos: {e}")
        return redirect(url_for('index'))

    if nivel_id == 0 or municipio_id == 0 or asunto_id == 0:
        flash("Selecciona valores válidos en los combos.")
        return redirect(url_for('index'))

    estatus_id = 1
    turno = int(datetime.now().timestamp()) % 10000

    datos = (
        curp, asunto_id, nivel_id, municipio_id, nombres,
        telefono, correo, datetime.now(), paterno, materno,
        celular, estatus_id, turno
    )

    try:
        db = Database()
        sql = """
        INSERT INTO solicitud_turno (
            curp, id_asunto, cve_nivel, cve_mun, nombre,
            tel, correo, fecha_creacion, paterno, materno,
            celular, id_estatus, turno
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.cursor.execute(sql, datos)
        db.conn.commit()
        
    except Exception as e:
        db.conn.rollback()
        flash(f"Error al registrar en la base de datos: {e}")
    finally:
        db.close()

    return render_template('descargando.html', curp=curp, turno=turno)


@app.route('/modificar-turno', methods=['GET', 'POST'])
def modificar_turno():
    datos = None
    municipios = []
    niveles = []
    asuntos = []

    exito = request.args.get('exito') 
    curp = request.args.get('curp')    
    turno = request.args.get('turno')  

    if request.method == 'POST':
        curp = request.form['curp']
        turno = request.form['turno']

        db = Database()
        sql = "SELECT * FROM solicitud_turno WHERE curp = %s AND turno = %s"
        db.cursor.execute(sql, (curp, turno))
        datos = db.cursor.fetchone()

        # Consultar catálogos
        
        db.cursor.execute("SELECT cve_mun, nombre_mun FROM municipios")
        municipios = db.cursor.fetchall()


        db.cursor.execute("SELECT cve_nivel, nivel FROM niveles")
        niveles = db.cursor.fetchall()

        db.cursor.execute("SELECT id_asunto, asunto FROM asuntos")
        asuntos = db.cursor.fetchall()

        db.close()

        if not datos:
            flash("No se encontró un registro con ese CURP y turno.")
            return redirect(url_for('modificar_turno'))
        
        if not exito:
            exito = None

    return render_template('modificar_turno.html', datos=datos, municipios=municipios, niveles=niveles, asuntos=asuntos, exito=exito, curp=curp)


@app.route('/guardar-cambios', methods=['POST'])
def guardar_cambios():
    curp = request.form['curp']
    turno = request.form['turno']
    nombres = request.form['nombres']
    paterno = request.form['paterno']
    materno = request.form['materno']
    telefono = request.form['telefono']
    correo = request.form['correo']
    municipio = request.form['municipio']
    nivel = request.form['nivel']
    asunto = request.form['asunto']

    db = Database()
    sql = """
        UPDATE solicitud_turno
        SET nombre = %s, paterno = %s, materno = %s, tel = %s, correo = %s,
            cve_mun = %s, cve_nivel = %s, id_asunto = %s
        WHERE curp = %s AND turno = %s
    """
    db.cursor.execute(sql, (nombres, paterno, materno, telefono, correo, municipio, nivel, asunto, curp, turno))
    db.conn.commit() 
    db.close()

    flash('¡Datos actualizados correctamente!')
    return redirect(url_for('modificar_turno', exito=1, curp=curp, turno=turno))

@app.route('/descargar-comprobante/<curp>')
def descargar_comprobante(curp):
    db = Database()

    sql = "SELECT nombre, paterno, materno, turno, tel, celular, correo, cve_nivel, cve_mun, id_asunto FROM solicitud_turno WHERE curp = %s"
    db.cursor.execute(sql, (curp,))
    resultado = db.cursor.fetchone()

    if not resultado:
        db.close()
        flash("No se encontró la información del turno.")
        return redirect(url_for('index'))

    nombre, paterno, materno, turno, telefono, celular, correo, cve_nivel, cve_mun, id_asunto = resultado

    
    sql_mun = "SELECT nombre_mun FROM municipios WHERE cve_mun = %s"
    db.cursor.execute(sql_mun, (cve_mun,))
    mun_result = db.cursor.fetchone()
    nombre_municipio = mun_result[0] if mun_result else "Municipio desconocido"

    sql_nivel = "SELECT nivel FROM niveles WHERE cve_nivel = %s"
    db.cursor.execute(sql_nivel, (cve_nivel,))
    nivel_result = db.cursor.fetchone()
    nombre_nivel = nivel_result[0] if nivel_result else "Nivel desconocido"

    sql_asunto = "SELECT asunto FROM asuntos WHERE id_asunto = %s"
    db.cursor.execute(sql_asunto, (id_asunto,))
    asunto_result = db.cursor.fetchone()
    nombre_asunto = asunto_result[0] if asunto_result else "Asunto desconocido"

    db.close()

    
    datos_usuario = {
        "curp": curp,
        "nombre": f"{nombre} {paterno} {materno}",
        "turno": turno,
        "telefono": telefono,
        "celular": celular,
        "correo": correo,
        "nivel": nombre_nivel,
        "municipio": nombre_municipio,
        "asunto": nombre_asunto
    }

    pdf_buffer = generar_comprobante_pdf(datos_usuario)

    return send_file(
        pdf_buffer,
        download_name=f"comprobante_{curp}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )



@app.route("/generar_qr")
def generar_qr():
    curp = request.args.get("curp")
    if not curp:
        return "Error: No se recibió la CURP", 400

    
    qr = qrcode.make(curp)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


@app.route('/admin-consultar')
def admin_consultar():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    db = Database()
    db.cursor.execute("""
        SELECT 
            st.curp, st.nombre, st.paterno, st.materno, st.tel, st.celular,
            st.correo, st.fecha_creacion, 
            a.asunto, m.nombre_mun, n.nivel, st.turno, st.id_estatus
        FROM solicitud_turno st
        JOIN asuntos a ON st.id_asunto = a.id_asunto
        JOIN municipios m ON st.cve_mun = m.cve_mun
        JOIN niveles n ON st.cve_nivel = n.cve_nivel
    """)
    solicitudes = db.cursor.fetchall()
    db.close()

    return render_template('admin-consultar.html', solicitudes=solicitudes)



@app.route('/admin-actualizar/<curp>', methods=['GET', 'POST'])
def admin_actualizar(curp):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    db = Database()

    if request.method == 'POST':
        nombre = request.form['nombre']
        tel = request.form['tel']
        correo = request.form['correo']
        paterno = request.form['paterno']
        materno = request.form['materno']
        celular = request.form['celular']
        id_estatus = request.form['id_estatus']

        update_sql = """
        UPDATE solicitud_turno
        SET nombre = %s, tel = %s, correo = %s, paterno = %s, materno = %s, celular = %s, id_estatus = %s
        WHERE curp = %s
        """
        db.cursor.execute(update_sql, (nombre, tel, correo, paterno, materno, celular, id_estatus, curp))
        db.conn.commit()
        db.close()
        flash("✅ Cambios guardados correctamente")
        return redirect(url_for('admin_actualizar', curp=curp))

    db.cursor.execute("""
        SELECT curp, nombre, tel, correo, paterno, materno, celular, id_estatus
        FROM solicitud_turno
        WHERE curp = %s
    """, (curp,))
    solicitud = db.cursor.fetchone()
    db.close()

    if solicitud:
        return render_template('admin-actualizar.html', solicitud=solicitud)
    else:
        return "Solicitud no encontrada", 404


@app.route('/admin-eliminar/<curp>')
def admin_eliminar(curp):
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    db = Database()

    # Eliminar por CURP
    db.cursor.execute("DELETE FROM solicitud_turno WHERE curp = %s", (curp,))
    db.conn.commit()
    db.close()

    return redirect(url_for('admin_consultar'))

@app.route('/admin-crear', methods=['GET', 'POST'])
def admin_crear():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))

    db = Database()

    if request.method == 'POST':
        # Recibir datos
        curp = request.form['curp']
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        tel = request.form['tel']
        celular = request.form['celular']
        correo = request.form['correo']
        id_asunto = int(request.form['id_asunto'])
        cve_nivel = int(request.form['cve_nivel'])
        cve_mun = int(request.form['cve_mun'])
        id_estatus = int(request.form['id_estatus'])  


        db.cursor.execute("SELECT MAX(turno) FROM solicitud_turno WHERE cve_mun = %s", (cve_mun,))
        ultimo_turno = db.cursor.fetchone()[0]
        turno = 1 if ultimo_turno is None else ultimo_turno + 1

        sql = """
        INSERT INTO solicitud_turno (
            curp, id_asunto, cve_nivel, cve_mun, nombre,
            tel, correo, fecha_creacion, paterno, materno,
            celular, id_estatus, turno
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos = (
            curp, id_asunto, cve_nivel, cve_mun, nombre,
            tel, correo, datetime.now(), paterno, materno,
            celular, id_estatus, turno
        )
        db.cursor.execute(sql, datos)
        db.conn.commit()
        db.close()

        return redirect(url_for('admin_consultar'))

    db.cursor.execute("SELECT * FROM asuntos")
    asuntos = db.cursor.fetchall()
    db.cursor.execute("SELECT * FROM municipios")
    municipios = db.cursor.fetchall()
    db.cursor.execute("SELECT * FROM niveles")
    niveles = db.cursor.fetchall()
    db.close()

    return render_template('admin-crear.html', asuntos=asuntos, municipios=municipios, niveles=niveles)

@app.route('/grafica')
def grafica():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('grafica2.html')


@app.route("/")
def data():
    try:
        connection = db = Database()
        with connection.cursor() as cursor:
            cursor.execute("SELECT categoria, cantidad FROM ventas")
            data = cursor.fetchall()
        connection.close()
        return jsonify(data)  # 💡 JSON siempre
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Manejo de errores

@app.route("/grafica2")
def get_chart_data2():
    return render_template('grafica2.html')

@app.route('/api/dashboard')
def api_dashboard():
    municipio = request.args.get('municipio', 'todos')
    db = Database()
    try:
        if municipio == 'todos':
            sql = """
            SELECT m.nombre_mun AS municipio,
            e.nombre AS estatus,
            COUNT(*) AS total
            FROM solicitud_turno s
            JOIN municipios m ON s.cve_mun = m.cve_mun
            JOIN estatus e ON s.id_estatus = e.id_estatus
            GROUP BY m.nombre_mun, e.nombre
            """
            db.cursor.execute(sql)
        else:
            sql = """
            SELECT m.nombre_mun AS municipio,
            e.nombre AS estatus,
            COUNT(*) AS total
            FROM solicitud_turno s
            JOIN municipios m ON s.cve_mun = m.cve_mun
            JOIN estatus e ON s.id_estatus = e.id_estatus
            WHERE m.cve_mun = %s
            GROUP BY m.nombre_mun, e.nombre
            """
            db.cursor.execute(sql, (municipio,))

        resultados = db.cursor.fetchall()
        db.close()

        data = []
        for fila in resultados:
            data.append({
                "municipio": fila[0],
                "estatus": fila[1],
                "total": fila[2]
            })
        return jsonify(data)
    except Exception as e:
        print("❌ ERROR EN API DASHBOARD:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/asuntos')
def ver_asuntos():
    db = Database()
    db.cursor.execute("SELECT id_asunto, asunto FROM asuntos")
    asuntos = db.cursor.fetchall()
    db.close()
    return render_template('asuntos.html', asuntos=asuntos)

@app.route('/asuntos/agregar', methods=['POST'])
def agregar_asunto():
    asunto = request.form['asunto']
    db = Database()
    db.cursor.execute("INSERT INTO asuntos (asunto) VALUES (%s)", (asunto,))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_asuntos'))

@app.route('/asuntos/editar/<int:id_asunto>', methods=['POST'])
def editar_asunto(id_asunto):
    nuevo_asunto = request.form['asunto']
    db = Database()
    db.cursor.execute("UPDATE asuntos SET asunto = %s WHERE id_asunto = %s", (nuevo_asunto, id_asunto))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_asuntos'))

@app.route('/asuntos/eliminar/<int:id_asunto>', methods=['POST'])
def eliminar_asunto(id_asunto):
    db = Database()
    db.cursor.execute("DELETE FROM asuntos WHERE id_asunto = %s", (id_asunto,))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_asuntos'))

@app.route('/municipios')
def ver_municipios():
    db = Database()
    db.cursor.execute("SELECT cve_mun, nombre_mun FROM municipios")
    municipios = db.cursor.fetchall()
    db.close()
    return render_template('municipios.html', municipios=municipios)

@app.route('/agregar-municipio', methods=['POST'])
def agregar_municipio():
    cve_mun = request.form['cve_mun']  
    nombre = request.form['nombre']

    db = Database()
    db.cursor.execute(
        "INSERT INTO municipios (cve_mun, nombre_mun) VALUES (%s, %s)",
        (cve_mun, nombre)
    )
    db.cursor.connection.commit()

    flash('Municipio agregado correctamente')
    return redirect(url_for('ver_municipios'))  

@app.route('/municipios/editar/<int:cve_mun>', methods=['POST'])
def editar_municipio(cve_mun):
    nuevo_nombre = request.form['nombre']
    db = Database()
    db.cursor.execute("UPDATE municipios SET nombre_mun = %s WHERE cve_mun = %s", (nuevo_nombre, cve_mun))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_municipios'))

@app.route('/municipios/eliminar/<int:cve_mun>', methods=['POST'])
def eliminar_municipio(cve_mun):
    db = Database()
    db.cursor.execute("DELETE FROM municipios WHERE cve_mun = %s", (cve_mun,))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_municipios'))

@app.route('/niveles')
def ver_niveles():
    db = Database()
    db.cursor.execute("SELECT cve_nivel, nivel FROM niveles")
    niveles = db.cursor.fetchall()
    db.close()
    return render_template('niveles.html', niveles=niveles)

@app.route('/niveles/agregar', methods=['POST'])
def agregar_nivel():
    nivel = request.form['nivel']
    db = Database()
    db.cursor.execute("INSERT INTO niveles (nivel) VALUES (%s)", (nivel,))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_niveles'))

@app.route('/niveles/editar/<int:cve_nivel>', methods=['POST'])
def editar_nivel(cve_nivel):
    nuevo_nivel = request.form['nivel']
    db = Database()
    db.cursor.execute("UPDATE niveles SET nivel = %s WHERE cve_nivel = %s", (nuevo_nivel, cve_nivel))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_niveles'))

@app.route('/niveles/eliminar/<int:cve_nivel>', methods=['POST'])
def eliminar_nivel(cve_nivel):
    db = Database()
    db.cursor.execute("DELETE FROM niveles WHERE cve_nivel = %s", (cve_nivel,))
    db.conn.commit()
    db.close()
    return redirect(url_for('ver_niveles'))



if __name__ == "__main__":
    app.run(debug=True)
