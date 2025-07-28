from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# -------------------------------
# 1. Cargar variables de entorno
# -------------------------------
# Ruta absoluta al archivo .env
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

# Obtener la URL de la base de datos desde la variable de entorno
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("❌ No se encontró la variable DATABASE_URL en el entorno.")

# -----------------------------------
# 2. Configuración del contexto Alembic
# -----------------------------------
config = context.config

# Sobrescribimos la URL con la del .env
config.set_main_option("sqlalchemy.url", database_url)

# Configurar logging si hay archivo definido
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------
# 3. Agregar carpeta 'src/' al sys.path
#    para permitir los imports
# ----------------------------------------
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# ----------------------------------------
# 4. Importar Base desde el módulo adecuado
#    Asegúrate de que Base esté bien definido ahí
# ----------------------------------------
from db.base import Base  # Ajusta este import si tu archivo base está en otra ruta

# Alembic usará esto para autogenerar migraciones
target_metadata = Base.metadata

# -------------------------------
# 5. Función modo OFFLINE
# -------------------------------
def run_migrations_offline():
    """Ejecuta migraciones sin una conexión activa a la base de datos."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------------
# 6. Función modo ONLINE
# -------------------------------
def run_migrations_online():
    """Ejecuta migraciones con una conexión activa a la base de datos."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# -------------------------------
# 7. Ejecutar según el modo
# -------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
