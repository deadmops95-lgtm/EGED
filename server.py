import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    logging.info("База данных успешно инициализирована.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"status": "Chronicles backend is running"}

class ChronicleCreate(BaseModel):
    user_id: int
    text: str
    time_slot: str | None = None
    date: str | None = None

class ChronicleToggle(BaseModel):
    task_id: int
    user_id: int

class SanctuaryCreate(BaseModel):
    user_id: int
    text: str

@app.get("/api/chronicles/{user_id}")
def get_chronicles(user_id: int):
    return database.get_user_chronicles(user_id)

@app.post("/api/chronicles")
def create_chronicle(item: ChronicleCreate):
    database.add_user_chronicle(item.user_id, item.text, item.time_slot, item.date)
    return {"status": "ok"}

@app.post("/api/chronicles/toggle")
def toggle_chronicle(data: ChronicleToggle):
    database.toggle_chronicle_status(data.task_id, data.user_id)
    return {"status": "ok"}

@app.get("/api/sanctuary/{user_id}")
def get_sanctuary(user_id: int):
    return database.get_user_sanctuary(user_id)

@app.post("/api/sanctuary")
def create_sanctuary(item: SanctuaryCreate):
    database.add_user_sanctuary(item.user_id, item.text, None)
    return {"status": "ok"}
