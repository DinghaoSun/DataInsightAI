from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to DataInsightAI"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "DataInsightAI"}