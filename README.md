# Blacklist Service — Microservicio Lista Negra de Emails

Microservicio REST desarrollado en Python + Flask para la gestión de una lista
negra global de emails. Entrega 1 del curso de DevOps (despliegue manual en AWS
Elastic Beanstalk).

## Stack

- Python 3.8+ / Flask
- Flask-SQLAlchemy (ORM)
- Flask-RESTful (API REST)
- Flask-Marshmallow (serialización)
- Flask-JWT-Extended (autorización por Bearer Token)
- PostgreSQL (AWS RDS) — en local usa SQLite automáticamente

## Endpoints

Ambos requieren la cabecera: `Authorization: Bearer <token>`

### POST /blacklists
Agrega un email a la lista negra.

Body (JSON):
```json
{
  "email": "cliente@ejemplo.com",
  "app_uuid": "11111111-2222-3333-4444-555555555555",
  "blocked_reason": "fraude reportado"
}
```
- `email` (obligatorio)
- `app_uuid` (obligatorio)
- `blocked_reason` (opcional, máx. 255 caracteres)

El servicio guarda además, por su cuenta: la IP de origen y la fecha/hora.

Respuesta: `201 Created`.

### GET /blacklists/&lt;email&gt;
Consulta si un email está en la lista negra.

Respuesta `200 OK`:
```json
{
  "email": "cliente@ejemplo.com",
  "blacklisted": true,
  "blocked_reason": "fraude reportado"
}
```

### GET /
Health check. Devuelve `200 OK` (lo usa Beanstalk para marcar el entorno sano).

## Ejecutar en local

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python application.py
```
La app queda en http://localhost:5000 y crea un archivo `blacklist.db` (SQLite).

## Configuración por variables de entorno

| Variable | Para qué |
|---|---|
| `STATIC_BEARER_TOKEN` | Token Bearer estático (si no se define, usa uno por defecto en local) |
| `JWT_SECRET_KEY` | Clave de firma JWT |
| `RDS_HOSTNAME`, `RDS_DB_NAME`, `RDS_USERNAME`, `RDS_PASSWORD`, `RDS_PORT` | Conexión a PostgreSQL en AWS (las inyecta Beanstalk al conectar RDS) |

Si no existen las variables `RDS_*`, la app usa SQLite local automáticamente.
