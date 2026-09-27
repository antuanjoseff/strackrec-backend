from . import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.cog import router as cog_router
from .routers.geofabrik import router as geofabrik_router
from .routers.mapes import router as mapes_router
from .routers.map_requests import router as map_requests_router

app = FastAPI(
    title="Servidor de Retalls COG",
    description="API per obtenir retalls de fitxers COG locals",
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["x-bbox", "x-width", "x-height", "Content-Disposition"],
)

app.include_router(cog_router)
app.include_router(geofabrik_router)
app.include_router(map_requests_router)
app.include_router(mapes_router)
