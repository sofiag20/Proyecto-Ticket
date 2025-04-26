from flask_bcrypt import check_password_hash
from models.Database import Database

def valida_admin(username, password):
    db = Database()
    sql = "SELECT * FROM admin_users WHERE username = %s AND password = %s"
    db.cursor.execute(sql, (username, password))
    result = db.cursor.fetchone()
    print("Resultado:", result)  # <-- esto es clave para saber si encontró algo
    db.close()
    return bool(result)

