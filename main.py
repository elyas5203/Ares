# main.py

import logging
import os
import ollama

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# ماژول‌های پروژه
from woocommerce_api import create_product_draft
from competitor_analysis import run_analysis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from product_manager import handle_new_product_submission
from woocommerce_api import get_product_categories # <-- وارد کردن تابع جدید

# --- توکن ربات تلگرام ---
# این توکن از فایل قبلی شما خوانده شده است.
TELEGRAM_BOT_TOKEN = "7557627836:AAEgfoM8VVZqwbblTSFLMeLRJUYieAMKrzI"

# --- تنظیمات ---
# پوشه‌ای برای ذخیره موقت عکس‌ها
TEMP_IMAGE_DIR = "temp_images"
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

# فعال کردن لاگ‌گیری برای مشاهده خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING) # کاهش لاگ‌های اضافی از کتابخانه HTTP

# --- توابع مربوط به دستورات ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start و نمایش راهنما."""
    welcome_message = (
        "سلام! من دستیار هوشمند «تحریرچی شاپ» هستم.\n\n"
        "می‌توانید از دستورات زیر استفاده کنید:\n\n"
        "📸 **افزودن محصول با عکس:**\n"
        "یک عکس از محصول ارسال کنید و نام محصول را در کپشن (متن زیر عکس) بنویسید.\n\n"
        "📝 **/addproduct** `نام;قیمت;توضیح`\n"
        "افزودن محصول به صورت متنی.\n\n"
        "📈 **/analyze**\n"
        "شروع تحلیل اولیه رقبا.\n\n"
        "🤖 **گفتگو با من:**\n"
        "هر پیام متنی دیگری را برای من ارسال کنید تا با هوش مصنوعی به شما پاسخ دهم."
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message
    )


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مرحله دوم: پردازش انتخاب دسته‌بندی کاربر و ایجاد محصول.
    """
    query = update.callback_query
    await query.answer() # پاسخ به تلگرام برای تایید دریافت کلیک

    callback_data = query.data
    category_id = None

    if callback_data == "cat_cancel":
        await query.edit_message_text(text="❌ عملیات لغو شد.")
        # پاک کردن اطلاعات موقت
        context.user_data.pop('product_name', None)
        context.user_data.pop('image_path', None)
        return

    if callback_data != "cat_misc":
        category_id = int(callback_data.split('_')[1])

    # بازیابی اطلاعات از user_data
    product_name = context.user_data.get('product_name')
    local_image_path = context.user_data.get('image_path')

    if not product_name or not local_image_path:
        await query.edit_message_text(text="⚠️ خطایی رخ داد. لطفاً دوباره عکس را ارسال کنید.")
        return

    await query.edit_message_text(text=f"✅ دسته‌بندی انتخاب شد. در حال ایجاد پیش‌نویس محصول «{product_name}»...")

    # فراخوانی تابع اصلی با شناسه دسته‌بندی مشخص
    result = handle_new_product_submission(local_image_path, product_name, category_id)

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

    # پاک کردن اطلاعات موقت
    context.user_data.pop('product_name', None)
    context.user_data.pop('image_path', None)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مرحله اول: دریافت عکس و نمایش دکمه‌های دسته‌بندی.
    """
    message = update.message
    photo = message.photo[-1]
    product_name = message.caption

    if not product_name:
        await message.reply_text("❌ **خطا:** لطفاً نام محصول را در کپشن (متن زیر عکس) وارد کنید.")
        return

    try:
        # دانلود و ذخیره موقت عکس
        file = await photo.get_file()
        file_extension = os.path.splitext(file.file_path)[1]
        local_image_path = os.path.join(TEMP_IMAGE_DIR, f"{file.file_id}{file_extension}")
        await file.download_to_drive(local_image_path)

        # ذخیره اطلاعات برای مرحله بعد
        context.user_data['product_name'] = product_name
        context.user_data['image_path'] = local_image_path

        # دریافت دسته‌بندی‌ها و ساخت دکمه‌ها
        categories = get_product_categories()
        if not categories:
            await message.reply_text("⚠️ نتوانستم لیست دسته‌بندی‌ها را از سایت دریافت کنم. لطفاً بعداً دوباره تلاش کنید.")
            return

        keyboard = [
            [InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")]
            for cat in categories
        ]
        # اضافه کردن دکمه "متفرقه" و "لغو"
        keyboard.append([InlineKeyboardButton("🗂️ متفرقه", callback_data="cat_misc")])
        keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cat_cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(
            f"✅ عکس برای محصول «{product_name}» دریافت شد.\n\n"
            f"لطفاً دسته‌بندی آن را انتخاب کنید:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logging.error(f"Error in handle_photo: {e}")
        await message.reply_text("یک خطای پیش‌بینی‌نشده در پردازش عکس رخ داد.")


async def analyze_competitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع تحلیل رقبا."""
    await update.message.reply_text("شروع فرآیند تحلیل رقبا... این ممکن است چند دقیقه طول بکشد.")
    try:
        results = run_analysis()
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


async def add_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور افزودن محصول به صورت متنی."""
    try:
        parts = ' '.join(context.args).split(';')
        if len(parts) < 3:
            await update.message.reply_text("لطفاً از فرمت صحیح استفاده کنید:\n/addproduct نام محصول; قیمت; توضیحات")
            return

        name, price, description = (p.strip() for p in parts)
        product_data = {'name': name, 'type': 'simple', 'regular_price': price, 'description': description}
        await update.message.reply_text("در حال ایجاد پیش‌نویس محصول... لطفاً صبر کنید.")
        result = create_product_draft(product_data)
        if result["success"]:
            response_text = f"{result['message']}\n\nبرای بازبینی و انتشار، روی لینک زیر کلیک کنید:\n{result['edit_link']}"
        else:
            response_text = f"خطا در ایجاد محصول: {result['message']}"
        await update.message.reply_text(response_text)
    except Exception as e:
        logging.error(f"Error in add_product_command: {e}")
        await update.message.reply_text("متاسفانه در پردازش درخواست شما خطایی رخ داد.")


async def llm_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ هوشمند به پیام‌های متنی."""
    user_message = update.message.text
    try:
        response = ollama.chat(model='llama3:latest', messages=[{'role': 'user', 'content': user_message}])
        ai_response = response['message']['content']
    except Exception as e:
        logging.error(f"Error communicating with Ollama: {e}")
        ai_response = "متاسفانه در ارتباط با مدل هوش مصنوعی خطایی رخ داد."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ai_response)


def main():
    """راه‌اندازی و اجرای ربات تلگرام."""
    print("در حال ساخت اپلیکیشن ربات...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # تعریف دستورات (هندلرها)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('addproduct', add_product_command))
    application.add_handler(CommandHandler('analyze', analyze_competitors_command))

    # --- هندلر جدید برای عکس ---
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # --- هندلر جدید برای دکمه‌های دسته‌بندی ---
    application.add_handler(CallbackQueryHandler(handle_category_selection))

    # هندلر پیام‌های متنی باید اولویت کمتری داشته باشد
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), llm_response))

    print("ربات با موفقیت شروع به کار کرد... برای توقف Ctrl+C را بزنید.")
    application.run_polling()

if __name__ == '__main__':
    main()
