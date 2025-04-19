from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = "7982505263:AAFgGEHwz-Nxza4WzwFiMMdmku0C6q81AP4"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🇺🇿 O'zbek"), KeyboardButton("🇷🇺 Русский")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("Iltimos, tilni tanlang / Пожалуйста, выберите язык:", reply_markup=keyboard)

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    user_id = update.effective_user.id
    user_data[user_id] = {"lang": lang}

    contact_btn = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number
    user_data[user_id]["phone"] = phone
    await update.message.reply_text("Endi ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in user_data and "phone" in user_data[user_id] and "name" not in user_data[user_id]:
        user_data[user_id]["name"] = text
        user_data[user_id]["id"] = f"A{len(user_data):02}"
        await update.message.reply_text(
            f"Ro'yxatdan o'tdingiz!\nSizning ID: {user_data[user_id]['id']}\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Lokatsiya qo'shish"), KeyboardButton("🔍 Qidirish")]],
                resize_keyboard=True
            )
        )

    elif text == "📍 Lokatsiya qo'shish":
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("📍 O‘zim turgan joy"), KeyboardButton("🏠 Uy manzili")],
            [KeyboardButton("🏢 Ish joyi")],
            [KeyboardButton("⬅️ Orqaga")]
        ], resize_keyboard=True)
        await update.message.reply_text("Qaysi lokatsiyani qo‘shmoqchisiz?", reply_markup=keyboard)

    elif text in ["📍 O‘zim turgan joy", "🏠 Uy manzili", "🏢 Ish joyi"]:
        user_data[user_id]["pending_location"] = text
        await update.message.reply_text("Iltimos, xaritada joylashuvingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]],
                resize_keyboard=True, one_time_keyboard=True
            )
        )

    elif text == "⬅️ Orqaga":
        await update.message.reply_text("Asosiy menyu:", reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Lokatsiya qo'shish"), KeyboardButton("🔍 Qidirish")]],
            resize_keyboard=True
        ))

    elif text == "🔍 Qidirish":
        await update.message.reply_text("Iltimos, ID ni kiriting (masalan: A01_H):")

    elif user_id in user_data and text.startswith("A") and ("_" in text):
        # qidiruv ID formati: A01_C, A01_H, A01_W
        for user in user_data.values():
            locations = user.get("locations", {})
            for loc in locations.values():
                if loc["id"] == text:
                    lat, lon = loc["lat"], loc["lon"]
                    await update.message.reply_location(latitude=lat, longitude=lon)
                    return
        await update.message.reply_text("Bunday ID topilmadi.")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data and "pending_location" in user_data[user_id]:
        label = user_data[user_id].pop("pending_location")
        lat = update.message.location.latitude
        lon = update.message.location.longitude

        if "locations" not in user_data[user_id]:
            user_data[user_id]["locations"] = {}

        label_code = {"📍 O‘zim turgan joy": "C", "🏠 Uy manzili": "H", "🏢 Ish joyi": "W"}
        loc_id = f"{user_data[user_id]['id']}_{label_code[label]}"
        user_data[user_id]["locations"][label] = {"lat": lat, "lon": lon, "id": loc_id}

        await update.message.reply_text(f"{label} saqlandi! ID: {loc_id}", reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Lokatsiya qo'shish"), KeyboardButton("🔍 Qidirish")]],
            resize_keyboard=True
        ))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(🇺🇿 O'zbek|🇷🇺 Русский)$"), handle_language))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    app.run_polling()

if __name__ == "__main__":
    main()
