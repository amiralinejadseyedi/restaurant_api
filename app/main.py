from fastapi import FastAPI

app = FastAPI(title="Restaurant API")


@app.get("/")
def home():
    return {"message":"restaurant api is running"}
