# api/__init__.py
from fastapi import APIRouter

from . import routes_upload, routes_predict, routes_metrics

api_router = APIRouter()
api_router.include_router(routes_upload.router)

api_router.include_router(routes_predict.router)

api_router.include_router(routes_metrics.router)
