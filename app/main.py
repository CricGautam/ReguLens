from fastapi import FastAPI

app = FastAPI(title="ReguLens API")


@app.get("/")
def root():
    return {"message": "ReguLens API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}