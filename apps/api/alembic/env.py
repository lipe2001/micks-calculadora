from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os
import sys

# >>>>>>> IMPORTANTE: garante que /app (pai de /app/alembic) está no sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /app
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# <<<<<<<

from app.core.database import Base
import app.models  # importa para preencher Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return os.getenv("DATABASE_URL", "postgresql+psycopg://micks:micks@db:5432/micks")

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
