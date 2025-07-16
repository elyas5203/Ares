# main.py

import logging
import os
import ollama
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# ماژول‌های پروژه
# فایل‌های ووکامرس و مدیریت محصول
from woocommerce_api import get_product_categories
from product_manager import handle_new_product_submission
# فایل تحلیل رقبا
from competitor_analysis import run_analysis
# فایل‌های تنظیمات
from woocommerce_api import WC_API_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET


# --- توکن ربات تلگرام ---
TELEGRAM_BOT_TOKEN = "7557627836:AAEgfoM8VVZqwbblTSFLMeLRJUYieAMKrzI"

# --- اطلاعات لاگین اینستاگرام ---
INSTAGRAM_USERNAME = "@test.elyas"
INSTAGRAM_PASSWORD = "Elyas_5203"

# --- تنظیمات کلی ---
TEMP_IMAGE_DIR = "temp_images"
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("instaloader").setLevel(logging.INFO)


# =================================================================
# --- توابع اصلی ربات ---
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start و نمایش راهنمای کامل."""
    welcome_message = (
        "سلام! من دستیار هوشمند «تحریرچی شاپ» هستم.\n\n"
        "قابلیت‌های من:\n\n"
        "📸 **افزودن محصول با عکس:**\n"
        "یک عکس از محصول ارسال کنید و نام محصول را در کپشن بنویسید. من از شما دسته‌بندی را خواهم پرسید.\n\n"
        "📝 **/addproduct** `نام; قیمت; توضیحات; [دسته‌بندی]`\n"
        "افزودن محصول به صورت متنی. دسته‌بندی اختیاری است.\n\n"
        "📈 **/analyze**\n"
        "تحلیل رقبا در وب و اینستاگرام.\n\n"
        "🩺 **/health**\n"
        "بررسی وضعیت اتصال به سرویس‌های حیاتی.\n\n"
        "🤖 **گفتگو با من:**\n"
        "هر پیام متنی دیگری را برای من ارسال کنید تا با هوش مصنوعی به شما پاسخ دهم. من مکالمات را به خاطر می‌سپارم!"
    )
    await update.message.reply_text(welcome_message)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مرحله ۱: دریافت عکس و نمایش دکمه‌های دسته‌بندی."""
    message = update.message
    photo = message.photo[-1]
    product_name = message.caption

    if not product_name:
        await message.reply_text("❌ **خطا:** لطفاً نام محصول را در کپشن (متن زیر عکس) وارد کنید.")
        return

    try:
        file = await photo.get_file()
        file_extension = os.path.splitext(file.file_path)[1]
        local_image_path = os.path.join(TEMP_IMAGE_DIR, f"{file.file_id}{file_extension}")
        await file.download_to_drive(local_image_path)

        context.user_data['product_name'] = product_name
        context.user_data['image_path'] = local_image_path

        categories = get_product_categories()
        if not categories:
            await message.reply_text("⚠️ نتوانستم لیست دسته‌بندی‌ها را از سایت دریافت کنم. لطفاً بعداً دوباره تلاش کنید.")
            return

        keyboard = [[InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")] for cat in categories]
        keyboard.append([InlineKeyboardButton("🗂️ متفرقه (بدون دسته‌بندی)", callback_data="cat_misc")])
        keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cat_cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(
            f"✅ عکس برای محصول «{product_name}» دریافت شد.\n\n"
            f"لطفاً دسته‌بندی آن را انتخاب کنید:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error in handle_photo_message: {e}")
        await message.reply_text("یک خطای پیش‌بینی‌نشده در پردازش عکس رخ داد.")


async def handle_category_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مرحله ۲: پردازش انتخاب دسته‌بندی کاربر و ایجاد محصول."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    category_id = None

    if callback_data == "cat_cancel":
        await query.edit_message_text(text="❌ عملیات لغو شد.")
        context.user_data.clear()
        return

    if callback_data != "cat_misc":
        category_id = int(callback_data.split('_')[1])

    product_name = context.user_data.get('product_name')
    local_image_path = context.user_data.get('image_path')

    if not product_name or not local_image_path:
        await query.edit_message_text(text="⚠️ خطایی رخ داد (اطلاعات محصول یافت نشد). لطفاً دوباره عکس را ارسال کنید.")
        return

    await query.edit_message_text(text=f"✅ دسته‌بندی انتخاب شد. در حال ایجاد پیش‌نویس برای «{product_name}»...")

    result = handle_new_product_submission(product_name=product_name, local_image_path=local_image_path, category_id=category_id)

    if result and result.get("success"):
        reply_message = (
            f"🎉 پیش‌نویس محصول با موفقیت ایجاد شد!\n\n"
            f"🔸 **نام محصول:** {product_name}\n"
            f"👇 برای تکمیل اطلاعات و انتشار، از لینک زیر استفاده کنید:\n"
            f"{result.get('edit_link')}"
        )
        await query.message.reply_text(reply_message)
    else:
        error_msg = result.get('message') if result else "یک خطای ناشناخته رخ داد."
        await query.message.reply_text(f"❗️ متاسفانه در ایجاد محصول خطایی رخ داد:\n\n{error_msg}")

    context.user_data.clear()


async def add_product_text_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور افزودن محصول به صورت متنی."""
    try:
        command_text = ' '.join(context.args)
        parts = [p.strip() for p in command_text.split(';')]

        if len(parts) < 3:
            await update.message.reply_text("فرمت صحیح:\n/addproduct نام; قیمت; توضیحات; [نام دسته‌بندی]")
            return

        name, price, description = parts[0], parts[1], parts[2]
        category_name = parts[3] if len(parts) > 3 else None

        await update.message.reply_text("در حال ایجاد پیش‌نویس محصول...")

        result = handle_new_product_submission(
            product_name=name,
            category_name=category_name,
            description=description,
            price=price
        )

        if result and result.get("success"):
            response_text = f"{result['message']}\n\nبرای بازبینی و انتشار، روی لینک زیر کلیک کنید:\n{result['edit_link']}"
        else:
            response_text = f"خطا در ایجاد محصول: {result.get('message', 'خطای ناشناخته')}"
        await update.message.reply_text(response_text)
    except Exception as e:
        logging.error(f"Error in add_product_text_command: {e}")
        await update.message.reply_text("متاسفانه در پردازش درخواست شما خطایی رخ داد.")


async def health_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی وضعیت اتصال به سرویس‌های حیاتی."""
    await update.message.reply_text("در حال بررسی وضعیت سیستم...")

    # بررسی ووکامرس
    wc_status = "❌ قطع"
    try:
        response = requests.get(f"{WC_API_URL.replace('/wc/v3/', '/wc/v3')}", auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET), timeout=10)
        if response.status_code == 200:
            wc_status = "✅ متصل"
    except Exception as e:
        logging.error(f"Health Check - WooCommerce Error: {e}")

    # بررسی Ollama
    ollama_status = "❌ قطع"
    try:
        ollama.list()
        ollama_status = "✅ متصل"
    except Exception as e:
        logging.error(f"Health Check - Ollama Error: {e}")

    report = (
        f"🩺 **گزارش وضعیت سیستم** 🩺\n\n"
        f"**WooCommerce API:** {wc_status}\n"
        f"**Ollama (Llama 3):** {ollama_status}\n\n"
        "اگر سرویسی قطع است، لطفاً موارد زیر را بررسی کنید:\n"
        "- **Ollama:** مطمئن شوید که سرویس Ollama روی کامپیوتر شما در حال اجرا است.\n"
        "- **WooCommerce:** از صحت کلیدهای API و اتصال اینترنت مطمئن شوید."
    )
    await update.message.reply_text(report)


async def llm_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ هوشمند با استفاده از Llama 3 و حافظه گفتگو."""
    user_message = update.message.text

    if 'history' not in context.user_data:
        context.user_data['history'] = []

    history = context.user_data['history']
    history.append({'role': 'user', 'content': user_message})
    context.user_data['history'] = history[-10:]

    try:
        response = ollama.chat(model='llama3:latest', messages=history)
        ai_response = response['message']['content']
        history.append({'role': 'assistant', 'content': ai_response})
        context.user_data['history'] = history[-10:]
    except Exception as e:
        logging.error(f"Error communicating with Ollama: {e}")
        ai_response = "متاسفانه در ارتباط با مدل هوش مصنوعی خطایی رخ داد."
        context.user_data['history'].pop()

    await update.message.reply_text(ai_response)


async def analyze_competitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع تحلیل رقبا."""
    await update.message.reply_text("شروع فرآیند تحلیل رقبا... این ممکن است چند دقیقه طول بکشد.")
    try:
        # پاس دادن اطلاعات لاگین به تابع
        results = run_analysis(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        response_text = "📊 **نتایج اولیه تحلیل رقبا** 📊\n\n"
        response_text += "🌐 **وب‌سایت‌ها:**\n"
        for site in results.get('websites', []):
            response_text += f"- {site['url']}: *{site['title']}*\n"
        response_text += "\n📱 **اینستاگرام:**\n"
        for profile in results.get('instagrams', []):
            response_text += f"- @{profile['username']} ({profile['followers']} دنبال‌کننده)\n"

        await update.message.reply_text("داده‌ها جمع‌آوری شد. در حال ارسال به مدل هوش مصنوعی برای دریافت پیشنهاد...")
        prompt = f"من یک فروشگاه لوازم تحریر آنلاین به نام 'تحریرچی شاپ' دارم. اطلاعات زیر از رقبای من جمع‌آوری شده است: {results}. بر اساس این داده‌ها، یک پیشنهاد اولیه و کلی برای بهبود وضعیت کسب‌وکار من ارائه بده."
        ollama_response = ollama.chat(model='llama3:latest', messages=[{'role': 'user', 'content': prompt}])
        suggestion = ollama_response['message']['content']
        final_response = response_text + "\n\n💡 **پیشنهاد هوش مصنوعی:**\n" + suggestion
        await update.message.reply_text(final_response, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in analyze_competitors_command: {e}")
        await update.message.reply_text("متاسفانه در فرآیند تحلیل خطایی رخ داد.")


def main():
    """راه‌اندازی و اجرای ربات تلگرام."""
    print("در حال ساخت اپلیکیشن ربات...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # ثبت دستورات
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('addproduct', add_product_text_command))
    application.add_handler(CommandHandler('analyze', analyze_competitors_command))
    application.add_handler(CommandHandler('health', health_check_command))

    # ثبت هندلرهای پیام
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    application.add_handler(CallbackQueryHandler(handle_category_selection_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), llm_chat_handler))

    print("ربات با موفقیت شروع به کار کرد... برای توقف Ctrl+C را بزنید.")
    application.run_polling()

if __name__ == '__main__':
    main()
