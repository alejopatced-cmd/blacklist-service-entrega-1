"""
schemas.py
----------
Serializacion con Flask-Marshmallow.

Un "schema" convierte un objeto Python (una fila Blacklist) en JSON para
devolverlo en la respuesta HTTP, y valida/convierte el JSON de entrada.
Es el puente entre el mundo Python y el JSON que viaja por la API.
"""
from flask_marshmallow import Marshmallow
from models import Blacklist

# Objeto global de Marshmallow. Se enlaza con la app en application.py.
ma = Marshmallow()


class BlacklistSchema(ma.SQLAlchemyAutoSchema):
    """
    Genera automaticamente los campos a partir del modelo Blacklist.
    Lo usamos para transformar registros de la BD en JSON de respuesta.
    """
    class Meta:
        model = Blacklist
        load_instance = True  # al deserializar, devuelve un objeto Blacklist


# Instancias listas para usar:
blacklist_schema = BlacklistSchema()          # para un solo registro
blacklists_schema = BlacklistSchema(many=True)  # para una lista de registros
