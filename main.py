import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import WebAppInfo
# --- Sozlamalar ---
BOT_TOKEN = "8184663205:AAHbnwXBHjXHueyOBqiFN7d3TcBmorqSheA"
WEB_APP_URL = "https://tamerkhan.uz/player2.html"
DB_PATH = "users.db"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# --- Reklama jarayon holatlari ---
class Reklama(StatesGroup):
    login = State()
    password = State()
    media = State()

# --- Matnlar ---
TEXTS = {
    "uz": {
        "choose": "Tilni tanlang:",
        "welcome": "👋 🇺🇿 Xush kelibsiz!\nBu yerda siz bepul va pullik telekanallarni\n— butunlay bepul tomosha qilishingiz mumkin.\nTomosha qilishni boshlash uchun «PLAY» ▶️ tugmasini bosing.",
        "auth_login": "Loginni kiriting:",
        "auth_pass": "Parolni kiriting:",
        "auth_fail": "Login yoki parol noto‘g‘ri. /reklama bilan qayta urinib ko‘ring.",
        "ask_media": "Reklama uchun bitta rasm va (ixtiyoriy) matn yuboring.",
        "broadcast": "Reklama yuborildi: muvaffaqiyatli={ok}, xatolik={bad}.",
        "users": "Foydalanuvchilar soni: {count}"
    },
    "ru": {
        "choose": "Выберите язык:",
        "welcome": "👋 🇷🇺 Добро пожаловать!\nЗдесь вы можете смотреть бесплатные и платные каналы бесплатно.\nНажмите «PLAY» ▶️ чтобы начать просмотр.",
        "auth_login": "Введите логин:",
        "auth_pass": "Введите пароль:",
        "auth_fail": "Неверный логин или пароль. Попробуйте снова /reklama.",
        "ask_media": "Отправьте одно фото рекламы и текст (по желанию).",
        "broadcast": "Реклама отправлена: успешно={ok}, ошибки={bad}.",
        "users": "Количество пользователей: {count}"
    },
    "kz": {
        "choose": "Тілді таңдаңыз:",
        "welcome": "👋 🇰🇿 Қош келдіңіз!\nМұнда тегін және ақылы каналдарды тегін көре аласыз.\nБастау үшін «PLAY» ▶️ басыңыз.",
        "auth_login": "Логин енгізіңіз:",
        "auth_pass": "Құпиясөз енгізіңіз:",
        "auth_fail": "Логин немесе құпиясөз қате. /reklama арқылы қайталаңыз.",
        "ask_media": "Рекламаның суретін және мәтінін жіберіңіз.",
        "broadcast": "Реклама жіберілді: сәтті={ok}, қате={bad}.",
        "users": "Пайдаланушылар саны: {count}"
    },
    "kg": {
        "choose": "Тилди тандаңыз:",
        "welcome": "👋 🇰🇬 Кош келиңиз!\nБул жерде акысыз жана акы төлөнүүчү каналдарды акысыз көрө аласыз.\nБаштоо үчүн «PLAY» ▶️ басыңыз.",
        "auth_login": "Логинди киргизиңиз:",
        "auth_pass": "Купуя сөздү киргизиңиз:",
        "auth_fail": "Логин же пароль туура эмес. /reklama менен кайрылыңыз.",
        "ask_media": "Рекламалык сүрөттү жана текстти жибериңиз.",
        "broadcast": "Реклама жөнөтүлдү: ийгиликтүү={ok}, ката={bad}.",
        "users": "Колдонуучулар саны: {count}"
    },
    "en": {
        "choose": "Choose language:",
        "welcome": "👋 🇺🇸 Welcome!\nHere you can watch free and paid channels — completely free.\nTo start watching press «PLAY» ▶️.",
        "auth_login": "Enter login:",
        "auth_pass": "Enter password:",
        "auth_fail": "Incorrect login or password. Use /reklama again.",
        "ask_media": "Send an ad photo and optional text.",
        "broadcast": "Broadcast finished: success={ok}, failed={bad}.",
        "users": "Number of users: {count}"
    }
}

# --- DB funksiyalar ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT)"
        )
        await db.commit()

async def add_user(user_id: int, lang="uz"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()

async def get_user_lang(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else "uz"

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users")
        rows = await cur.fetchall()
        return [r[0] for r in rows]

async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        r = await cur.fetchone()
        return r[0] or 0

# --- Tugmalar ---
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="lang_kz"),
         InlineKeyboardButton(text="🇰🇬 Кыргыз", callback_data="lang_kg"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

def play_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="«PLAY» ▶️", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])

# --- Start ---
@router.message(Command("start"))
async def start_cmd(msg: Message):
    await add_user(msg.from_user.id)
    await msg.answer(TEXTS["uz"]["choose"], reply_markup=lang_keyboard())

@router.callback_query(F.data.startswith("lang_"))
async def lang_choice(cb: CallbackQuery):
    code = cb.data.split("_")[1]
    await add_user(cb.from_user.id, code)
    # ⬇️ Til tanlash xabarini o'chirib tashlash
    await cb.message.delete()
    # Xush kelibsiz xabarini yuborish
    await cb.message.answer(TEXTS[code]["welcome"], reply_markup=play_button())
    await cb.answer()

# --- Usersall ---
@router.message(Command("usersall"))
async def users_all(msg: Message):
    lang = await get_user_lang(msg.from_user.id)
    count = await count_users()
    await msg.answer(TEXTS[lang]["users"].format(count=count))

# --- Reklama ---
@router.message(Command("reklama"))
async def reklama_start(msg: Message, state: FSMContext):
    lang = await get_user_lang(msg.from_user.id)
    await msg.answer(TEXTS[lang]["auth_login"])
    await state.set_state(Reklama.login)

@router.message(Reklama.login)
async def reklama_login(msg: Message, state: FSMContext):
    await state.update_data(login=msg.text.strip())
    lang = await get_user_lang(msg.from_user.id)
    await msg.answer(TEXTS[lang]["auth_pass"])
    await state.set_state(Reklama.password)

@router.message(Reklama.password)
async def reklama_pass(msg: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("login") == "admin" and msg.text.strip() == "admin":
        lang = await get_user_lang(msg.from_user.id)
        await msg.answer(TEXTS[lang]["ask_media"])
        await state.set_state(Reklama.media)
    else:
        lang = await get_user_lang(msg.from_user.id)
        await msg.answer(TEXTS[lang]["auth_fail"])
        await state.clear()

@router.message(Reklama.media, F.photo)
async def reklama_media(msg: Message, state: FSMContext):
    photo_id = msg.photo[-1].file_id
    caption = msg.caption or ""
    users = await get_all_users()
    ok, bad = 0, 0
    for uid in users:
        try:
            await bot.send_photo(uid, photo=photo_id, caption=caption)
            ok += 1
            await asyncio.sleep(0.05)
        except:
            bad += 1
    lang = await get_user_lang(msg.from_user.id)
    await msg.answer(TEXTS[lang]["broadcast"].format(ok=ok, bad=bad))
    await state.clear()

@router.message(Reklama.media)
async def reklama_not_photo(msg: Message):
    lang = await get_user_lang(msg.from_user.id)
    await msg.answer(TEXTS[lang]["ask_media"])

# --- Foydalanuvchini saqlash ---
@router.message()
async def catch_all(msg: Message):
    await add_user(msg.from_user.id)

# --- Bot ishga tushirish ---
async def main():
    await init_db()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
