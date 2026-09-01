from fastapi import FastAPI

app = FastAPI(
    title="DomoVida API",
    description="Backend para monitoreo de adultos mayores",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"mensaje": "DomoVida API funcionando"}
