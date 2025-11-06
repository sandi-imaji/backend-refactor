from fastapi import FastAPI
from app.routes.dataset_routes import datasetRouter
import uvicorn

app = FastAPI(title="Smart AI")

app.include_router(datasetRouter)


if __name__ == "__main__": uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
