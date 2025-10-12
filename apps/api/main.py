from fastapi import FastAPI
import os

app = FastAPI(title="Micks Calculadora API")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "api",
        "database_url_present": bool(os.getenv("DATABASE_URL")),
        "mailhog": {
            "host": os.getenv("MAILHOG_SMTP_HOST", "mail"),
            "port": int(os.getenv("MAILHOG_SMTP_PORT", "1025")),
        },
    }
