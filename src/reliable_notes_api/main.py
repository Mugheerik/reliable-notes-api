from fastapi import FastAPI

app = FastAPI(title="Reliable Notes API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Reliable Notes API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}