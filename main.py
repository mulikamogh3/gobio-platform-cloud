from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # <-- We are importing uvicorn directly now
from database import engine
import models
from routers import device
from routers import prediction

# Safely create tables during startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL GoBioAI Vault connected and tables verified.")
    yield

app = FastAPI(title="Milk Pasteurization IoT Backend", lifespan=lifespan)

# CORS Middleware (The Bridge)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device.router)
app.include_router(prediction.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Milk Pasteurization IoT Backend API"}
