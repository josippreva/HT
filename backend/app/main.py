from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.database import engine, Base
import app.models

from app.api.auth import router as auth_router
from app.api.master_data import router as master_data_router
from app.api.location import router as location_router
from app.api.devices import router as devices_router

from app.api.area_codes import router as area_codes_router

from app.api.rak_number_blocks import router as rak_number_blocks_router

from app.api.number_ranges import router as number_ranges_router
from app.api.subscribers import router as subscribers_router
from app.api.phone_numbers import router as phone_numbers_router
from app.api.dashboard import router as dashboard_router
from app.api.cities import router as cities_router
from app.api.regions import router as regions_router

app = FastAPI(
    title="HT Mostar API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Privremeno za razvoj; kasnije ćemo prijeći na Alembic migracije
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(master_data_router)
app.include_router(location_router)
app.include_router(devices_router)
app.include_router(area_codes_router)
app.include_router(rak_number_blocks_router)
app.include_router(number_ranges_router)
app.include_router(subscribers_router)
app.include_router(phone_numbers_router)
app.include_router(dashboard_router)
app.include_router(cities_router)
app.include_router(regions_router)

@app.get("/")
def root():
    return {"message": "API radi"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database": "connected",
        "result": value,
    }