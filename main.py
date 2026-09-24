import asyncio
import logging
import os
import shutil
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
import pytesseract

import database

# Ваш токен от BotFather
TOKEN = "8613062226:AAGzEqGz0j42I9ZrAyaxivMMqeW_4bir4N4"  

# Укажите адрес вашего сайта с Bothost (без слэша на конце)
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
async def create_sanctuary(
    user_id: int = Form(...),
    text: str = Form(""),
    file: UploadFile = File(None)
):
    image_url = None
    recognized_text = ""

    if file:
        file_extension = file.filename.split(".")[-1]
        file_name = f"{user_id}_{os.urandom(4).hex()}.{file_extension}"
        file_path = os.path.join("static/uploads", file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image_url = f"/static/uploads/{file_name}"

        try:
            img = Image.open(file_path)
            recognized_text = pytesseract.image_to_string(img, lang='rus+eng').strip()
        except Exception as e:
            logging.error(f"OCR Error: {e}")

    full_text = text
    if recognized_text:
        full_text += f"\n\n[Распознанный текст с изображения]:\n{recognized_text}"

    database.add_user_sanctuary(user_id, full_text, image_url)
    return {"status": "ok", "recognized": recognized_text}

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
