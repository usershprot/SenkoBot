import asyncio import aiohttp import json import os import hashlib from bs4 import BeautifulSoup from aiogram import Bot, Dispatcher, types from aiogram.filters import CommandStart, Command from aiogram.types import ( InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent )

API_TOKEN = "7922157529:AAGbfMgER0jagKEBXwdX6yaE0q2IihDW5N0"  # Заменить на токен от BotFather DATA_FILE = "search_data.json"

bot = Bot(token=API_TOKEN) dp = Dispatcher()

--- Работа с данными ---

def load_data(): if not os.path.exists(DATA_FILE): return {"history": {}, "top": {}} with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(data): with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

def update_history(user_id, query): data = load_data() history = data["history"].get(str(user_id), []) if query in history: history.remove(query) history.insert(0, query) data["history"][str(user_id)] = history[:10] data["top"][query] = data["top"].get(query, 0) + 1 save_data(data)

def get_user_history(user_id): data = load_data() return data["history"].get(str(user_id), [])

def get_top_queries(): data = load_data() top = sorted(data["top"].items(), key=lambda x: -x[1]) return top[:5]

--- Поиск на notanime.ru ---

async def search_anime(query: str): search_url = f"https://notanime.ru/?s={query.replace(' ', '+')}" async with aiohttp.ClientSession() as session: async with session.get(search_url) as resp: if resp.status != 200: return [] html = await resp.text()

soup = BeautifulSoup(html, "html.parser")
results = []
for card in soup.select(".anime-card"):
    try:
        title = card.select_one(".anime-title").text.strip()
        url = card.select_one("a")["href"]
        image = card.select_one("img")["src"]
        results.append({"title": title, "url": url, "image": image})
    except:
        continue
return results

async def get_anime_details(url): async with aiohttp.ClientSession() as session: async with session.get(url) as resp: if resp.status != 200: return None html = await resp.text() soup = BeautifulSoup(html, "html.parser") desc = soup.select_one(".anime-description") description = desc.text.strip() if desc else "Описание отсутствует" iframe = soup.find("iframe") iframe_url = iframe["src"] if iframe else "" return {"description": description, "iframe": iframe_url}

--- Команды ---

@dp.message(CommandStart()) async def start_cmd(message: Message): await message.answer("Привет! Напиши название аниме или его код, и я найду его на notanime.ru")

@dp.message(Command("history")) async def history_cmd(message: Message): history = get_user_history(message.from_user.id) if not history: await message.answer("История пуста.") else: text = "\n".join(f"• {q}" for q in history) await message.answer(f"🕘 История поиска:\n{text}")

@dp.message(Command("top")) async def top_cmd(message: Message): top = get_top_queries() if not top: await message.answer("Топ запросов пуст.") else: text = "\n".join(f"{i+1}. {q} — {c}" for i, (q, c) in enumerate(top)) await message.answer(f"🔥 Топ запросов дня:\n{text}")

--- Обработка обычного поиска ---

@dp.message() async def handle_search(message: Message): query = message.text.strip() update_history(message.from_user.id, query) results = await search_anime(query) if not results: await message.answer("❌ Ничего не найдено.") return

kb = [[InlineKeyboardButton(text=anime['title'], callback_data=anime['url'])] for anime in results[:10]]
await message.answer("🔎 Найдено:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

--- Обработка кнопок ---

@dp.callback_query() async def handle_details(call: CallbackQuery): url = call.data details = await get_anime_details(url) if not details: await call.message.answer("Ошибка при получении данных.") return

text = f"📄 *Описание:*\n{details['description']}\n\n[📺 Перейти на сайт]({url})"
await call.message.answer(text, parse_mode="Markdown")

--- Инлайн-поиск ---

@dp.inline_query() async def inline_query_handler(query: InlineQuery): text = query.query.strip() if not text: return

results = []
found = await search_anime(text)
for anime in found[:10]:
    url = anime["url"]
    results.append(
        InlineQueryResultArticle(
            id=hashlib.md5(url.encode()).hexdigest(),
            title=anime["title"],
            description="Перейти на notanime.ru",
            input_message_content=InputTextMessageContent(
                message_text=f"🎬 [{anime['title']}]({url})",
                parse_mode="Markdown"
            ),
            thumb_url=anime["image"]
        )
    )
await query.answer(results, cache_time=1)

--- Запуск бота ---

async def main(): await dp.start_polling(bot)

if name == "main": asyncio.run(main())

