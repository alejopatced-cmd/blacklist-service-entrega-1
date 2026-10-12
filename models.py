"""
models.py
---------
Define la ESTRUCTURA de la tabla en la base de datos usando Flask-SQLAlchemy.

Un "modelo" es una clase de Python que representa una tabla. Cada atributo
de la clase es una columna. SQLAlchemy (el ORM) traduce esto a SQL por
nosotros: crear la tabla, insertar filas, consultar... sin escribir SQL a mano.
"""
from flask_sqlalchemy import SQLAlchemy

# Objeto global de base de datos. Se "enlaza" con la app en application.py.
db = SQLAlchemy()


class Blacklist(db.Model):
    """
    Tabla 'blacklist': cada fila es un email bloqueado en la lista negra global.
    """
    __tablename__ = "blacklist"

    # Clave primaria autoincremental (id interno de cada registro).
    id = db.Column(db.Integer, primary_key=True)

    # Email bloqueado. index=True acelera las busquedas por email (el GET).
    email = db.Column(db.String(255), nullable=False, index=True)

    # UUID obligatorio de la app cliente que pidio el bloqueo.
    app_uuid = db.Column(db.String(255), nullable=False)

    # Motivo del bloqueo. Opcional (puede ser nulo), maximo 255 caracteres.
    blocked_reason = db.Column(db.String(255), nullable=True)

    # --- Datos que el microservicio guarda por su cuenta (no los envia el cliente) ---

    # IP de origen de la solicitud que creo el bloqueo.
    ip_address = db.Column(db.String(45), nullable=True)  # 45 caracteres cubre IPv6

    # Fecha y hora en que se registro el bloqueo.
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        # Representacion util para depurar.
        return f"<Blacklist {self.email}>"
