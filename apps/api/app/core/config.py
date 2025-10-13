import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://micks:micks@db:5432/micks")
MAILHOG_SMTP_HOST = os.getenv("MAILHOG_SMTP_HOST", "mail")
MAILHOG_SMTP_PORT = int(os.getenv("MAILHOG_SMTP_PORT", "1025"))