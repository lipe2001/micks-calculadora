from fastapi import FastAPI

app = FastAPI(title="Micks Calculadora WEB")

@app.get("/health")
def health():
    return {"status": "ok", "service": "web"}
