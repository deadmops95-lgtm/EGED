import asyncio
import logging
import os
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

import database

TOKEN = "8613062226:AAGzEqGz0j42I9ZrAyaxivMMqeW_4bir4N4"  
WEBAPP_URL = "ЗДЕСЬ_УКАЖИТЕ_АДРЕС_ВАШЕГО_САЙТА_С_BOTHOST"  

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()

os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChronicleCreate(BaseModel):
    user_id: int
    text: str
    time_slot: str
    date: str

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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏛️ Открыть Хроники", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "Добро пожаловать в уединенное пространство.\n\n"
        "Здесь вы можете упорядочить свои дни и остаться наедине с мыслями. Нажмите кнопку ниже:",
        reply_markup=kb
    )

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())
