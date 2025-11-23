# app.py (в корне проекта)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api_router

app = FastAPI(title="Coal Fire Prediction API")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
