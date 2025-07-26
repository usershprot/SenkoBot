import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8333111223:AAFDHMtpGkrNV3CVeAwUHkEIkYcNtbxY5fQ"

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_dice(emoji="🎲")
    value = message.dice.value
    await update.message.reply_text(f"🎲 Ты бросил кости: {value}")

async def darts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_dice(emoji="🎯")
    value = message.dice.value
    await update.message.reply_text(f"🎯 Ты бросил дротик: {value}")

async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_dice(emoji="🎰")
    value = message.dice.value
    # Например, считаем выигрыш если value == 64 (джекпот)
    if value == 64:
        result = "🎉 Джекпот! Ты выиграл!"
    else:
        result = f"🎰 Барабан остановился на: {value} — не повезло."
    await update.message.reply_text(result)

async def mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("5 мин", callback_data="mines_count_5"),
            InlineKeyboardButton("10 мин", callback_data="mines_count_10"),
            InlineKeyboardButton("15 мин", callback_data="mines_count_15")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💣 Сколько мин ты хочешь?",
        reply_markup=reply_markup
    )

async def mines_choose_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mines_count = int(query.data.split("_")[2])
    size = 5
    context.user_data['mines'] = random.sample(range(size * size), mines_count)

    keyboard = []
    for i in range(size):
        row = []
        for j in range(size):
            index = i * size + j
            row.append(InlineKeyboardButton("⬜️", callback_data=f"mine_{index}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"💣 Поле готово! Мин: {mines_count}. Выбирай клетку:",
        reply_markup=reply_markup
    )

async def mines_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data.split("_")[1])
    mines = context.user_data.get('mines', [])
    if index in mines:
        await query.edit_message_text("💥 Бум! Ты подорвался.")
    else:
        await query.edit_message_text("✅ Чисто! Повезло.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я казино-бот.\n"
        "/dice - бросить кости\n"
        "/darts - бросить дартс\n"
        "/slot - крутануть слот-машину\n"
        "/mines - сыграть в мины"
    )

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("darts", darts))
    app.add_handler(CommandHandler("slot", slot))
    app.add_handler(CommandHandler("mines", mines))
    app.add_handler(CallbackQueryHandler(mines_choose_count, pattern=r"^mines_count_"))
    app.add_handler(CallbackQueryHandler(mines_button, pattern=r"^mine_"))

    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()