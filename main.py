import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

import database

TOKEN = "8613062226:AAGzEqGz0j42I9ZrAyaxivMMqeW_4bir4N4"  
WEBAPP_URL = "https://bot-1790210796-8710-prokudin95.bothost.tech"  

bot = Bot(token=TOKEN)
dp = Dispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    # Запускаем поллинг бота в фоновой задаче
    asyncio.create_task(dp.start_polling(bot))
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

# Гарантированный запуск через uvicorn, если файл вызывается напрямую
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
