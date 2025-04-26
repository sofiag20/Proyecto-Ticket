import pymysql

class Database:
    _instance = None 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                cls._instance.conn = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='12345',
                    db='ticket_turno'
                )
                cls._instance.cursor = cls._instance.conn.cursor()
                print("Conexión exitosa (singleton)")
            except Exception as e:
                print("Error en la conexión:", e)
                cls._instance = None
        return cls._instance

    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        print("Conexión cerrada")
        Database._instance = None  # Reinicia la instancia singleton
