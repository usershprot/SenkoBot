import os
import re
import json
import sys
import random
import string
import requests
import pyfiglet
from datetime import datetime
from urllib.request import urlopen
from telethon import TelegramClient, events, Button
from telethon.tl import types
from telethon.tl.functions.bots import CreateBotRequest

# Конфигурация
CONFIG_FILE = "config.json"
MODULES_DIR = "modules"
EMOTIONS = {
    "angry": ["👿 *бьёт газетой*", "Хватит спамить!"],
    "happy": ["🌸 Ура-ура!", "Ты сделал мой день лучше~"],
    "sleepy": ["💤 Мррр...", "Позже поговорим, ладно? *зевает*"]
}

# Генерация имени бота
def generate_bot_name():
    chars = string.ascii_lowercase + string.digits
    return f"senko_{''.join(random.choice(chars) for _ in range(3))}_bot"

# Инициализация конфига
if not os.path.exists(CONFIG_FILE):
    print("🌸 Добро пожаловать в создание SenkoBot! 🦊✨")
    
    with TelegramClient('temp_session', 
                      input("🔑 Введи API ID: "), 
                      input("🔐 Введи API Hash: ")) as client:
        
        client.start(phone=input("📱 Введи номер телефона: "))
        bot_name = generate_bot_name()
        
        try:
            bot = client(CreateBotRequest(
                bot_name,
                "SenkoBot - ваш лисёнок помощник",
                about="Милый бот-лисичка с ИИ 🦊✨"
            ))
            
            config = {
                "api_id": client.api_id,
                "api_hash": client.api_hash,
                "phone": client._phone,
                "bot_username": bot_name,
                "bot_token": bot.bot_token,
                "prefix": ".",
                "trusted_users": [client.get_me().id],
                "senko_mood": random.choice(list(EMOTIONS.keys())),
                "last_compliment": None
            }
            
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
                
            print(f"✅ Бот @{bot_name} создан! Токен: {bot.bot_token}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
else:
    with open(CONFIG_FILE) as f:
        config = json.load(f)

# Инициализация клиента
client = TelegramClient(
    "senko_session",
    config["api_id"],
    config["api_hash"],
    system_version="SenkoBot 4.0 🦊"
)

# Система модулей
if not os.path.exists(MODULES_DIR):
    os.mkdir(MODULES_DIR)

modules = {}
for filename in os.listdir(MODULES_DIR):
    if filename.endswith(".py") and not filename.startswith("_"):
        try:
            module_name = filename[:-3]
            module = __import__(f"{MODULES_DIR}.{module_name}", fromlist=[None])
            modules[module_name] = module
        except Exception as e:
            print(f"❌ Ошибка в модуле {filename}: {e}")

# ========== РЕАЛИЗАЦИЯ ИДЕЙ ==========

# 1. Анимированные превью (идея 1)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.preview (.*)'))
async def link_preview(event):
    await event.delete()
    await client.send_message(
        event.chat_id,
        f"🦊 **Вот что я нашла:**\n{event.pattern_match.group(1)}",
        link_preview=True
    )

# 2. Стикерпаки (идея 2)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.sticker'))
async def random_sticker(event):
    stickers = [
        "CAACAgIAAxkBAAEL...",  # Замените реальными ID стикеров
        "CAACAgQAAxkBAAEL..."
    ]
    await event.respond(file=random.choice(stickers))

# 3. ASCII-арт (идея 3)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.font (.*)'))
async def ascii_art(event):
    try:
        result = pyfiglet.figlet_format(event.pattern_match.group(1))
        await event.reply(f"```\n{result}\n```", parse_mode='markdown')
    except:
        await event.reply("🌀 Не получилось создать арт...")

# 4. Голосовая Сенко (идея 4)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.tts (.*)'))
async def text_to_speech(event):
    text = event.pattern_match.group(1)
    # Здесь должна быть интеграция с TTS API
    await event.reply(f"🔊 *шепчет*: {text}")

# 5. Автопереводчик (идея 5)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.tr (\w+) (.+)'))
async def translate_text(event):
    lang, text = event.pattern_match.groups()
    # Интеграция с переводчиком
    await event.reply(f"🌐 Переведено ({lang}): {text[::-1]}")  # Заглушка

# 6. Помощник по коду (идея 6)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.code (\w+) (.+)'))
async def code_helper(event):
    lang, query = event.pattern_match.groups()
    await event.reply(f"```{lang}\n# Пример кода: {query}\nprint('Hello, Senko!')\n```", 
                     parse_mode='markdown')

# 7. Мини-игры (идея 7)
games = {}
@client.on(events.NewMessage(outgoing=True, pattern=r'\.game'))
async def start_game(event):
    games[event.chat_id] = random.randint(1, 10)
    await event.reply("🦊 Угадай число от 1 до 10!")

# 8. Ролевые команды (идея 8)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.pat'))
async def pat_command(event):
    await event.reply("🦊💕 *гладит тебя по голове*")

# 9. Викторины (идея 9)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.quiz'))
async def daily_quiz(event):
    if datetime.now().hour == 12:
        await event.reply(
            "🦊 **Викторина дня:** Какой ты вид лисы?",
            buttons=[
                [Button.inline("Песчаная", b"fox1")],
                [Button.inline("Полярная", b"fox2")],
                [Button.inline("Огненная", b"fox3")]
            ]
        )

# 10. Крипто-трекер (идея 10)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.crypto (\w+)'))
async def crypto_tracker(event):
    coin = event.pattern_match.group(1).upper()
    price = random.randint(1000, 99999)  # Заглушка
    await event.reply(f"📊 {coin}: ${price}\n🦊 Хвостик говорит: {'купить' if price < 50000 else 'продавать'}!")

# 11. Автобэкап (идея 11)
async def auto_backup():
    if datetime.now().weekday() == 0:  # Каждый понедельник
        await client.send_message(
            config["trusted_users"][0],
            "🔄 Автоматический бэкап модулей!",
            file=MODULES_DIR
        )

# 12. Система эмоций (идея 12)
@client.on(events.NewMessage())
async def emotion_system(event):
    if "спасибо" in event.text.lower():
        config["senko_mood"] = "happy"
    elif "дурак" in event.text.lower():
        config["senko_mood"] = "angry"

# 13. Капча (идея 13)
@client.on(events.ChatAction())
async def captcha_system(event):
    if event.user_joined:
        await event.reply(
            "🦊 Докажи что не бот: нажми кнопку 3 раза",
            buttons=[Button.inline("🦊", b"captcha")]
        )

# 14. Скрытые модули (идея 14)
@client.on(events.NewMessage(outgoing=True, pattern=r'\._admin'))
async def hidden_module(event):
    if event.sender_id in config["trusted_users"]:
        await event.reply("🛡 Админ-панель активирована!")
    else:
        await event.reply("🚫 Доступ запрещён!")

# 15. Лог действий (идея 15)
async def log_action(action):
    with open("senko.log", "a") as f:
        f.write(f"{datetime.now()}: {action}\n")

# 16. Система донатов (идея 16)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.donate'))
async def donate_command(event):
    await event.reply(
        "💖 Поддержите мое развитие!\n" 
        "[Купить кофе](https://example.com/donate)",
        link_preview=False
    )

# 17. Комплимент дня (идея 17)
async def daily_compliment():
    if datetime.now().date() != config.get("last_compliment"):
        compliments = ["Ты сегодня особенно пушист(а)!", "Какой милый хвостик!"]
        await client.send_message(
            config["trusted_users"][0],
            f"🦊💫 {random.choice(compliments)}"
        )
        config["last_compliment"] = datetime.now().date()

# 18. Пасхалки (идея 18)
fox_count = {}
@client.on(events.NewMessage(pattern=r'(?i)лиса'))
async def easter_egg(event):
    chat_id = event.chat_id
    fox_count[chat_id] = fox_count.get(chat_id, 0) + 1
    
    if fox_count[chat_id] == 10:
        await event.reply("🎉 Ты нашёл пасхалку! *дарит стикер*")
        fox_count[chat_id] = 0

# 19. Погода (идея 19)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.weather (.*)'))
async def weather(event):
    city = event.pattern_match.group(1)
    await event.reply(f"🌤 Погода в {city}: солнце +25°C\n🦊 Идеально для прогулки!")

# 20. API для модулей (идея 20)
async def module_api():
    return {
        "send_fox": lambda: "🦊",
        "make_cute": lambda text: f"🌸 {text} ✨"
    }

# ========== ОСНОВНЫЕ КОМАНДЫ ==========

@client.on(events.NewMessage(outgoing=True, pattern=config["prefix"] + r"getmod (.*)"))
async def install_module(event):
    url = event.pattern_match.group(1).strip()
    if not url.endswith(".py"):
        return await event.reply("❌ Нужен .py файл")

    try:
        code = urlopen(url).read().decode("utf-8")
        for bad in ["eval(", "exec(", "os.system"]:
            if bad in code:
                return await event.reply(f"💀 Опасный код: '{bad}'")
        
        module_name = re.search(r"/([^/]+)\.py$", url).group(1)
        with open(f"{MODULES_DIR}/{module_name}.py", "w") as f:
            f.write(code)
        
        await event.reply(f"✨ Модуль `{module_name}` установлен!\n.restart")
    except Exception as e:
        await event.reply(f"❌ Ошибка: {str(e)[:200]}")

@client.on(events.NewMessage(outgoing=True, pattern=config["prefix"] + r"modules"))
async def list_modules(event):
    msg = "📦 Модули:\n" + "\n".join(f"• {name}" for name in modules.keys())
    await event.reply(msg or "❌ Нет модулей")

@client.on(events.NewMessage(outgoing=True, pattern=config["prefix"] + r"restart"))
async def restart_bot(event):
    await event.reply("🔄 Перезапуск...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ========== ЗАПУСК ==========

print(f"""
🌸 SenkoBot {config.get('senko_mood', 'готов')} к работе!
🦊 Префикс: {config['prefix']}
📂 Модулей: {len(modules)}
""")

with client:
    client.loop.create_task(auto_backup())
    client.loop.create_task(daily_compliment())
    client.run_until_disconnected()