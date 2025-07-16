# main.py

import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# توکن ربات تلگرام خود را در اینجا قرار دهید
TELEGRAM_BOT_TOKEN = "7557627836:AAEgfoM8VVZqwbblTSFLMeLRJUYieAMKrzI"

# فعال کردن لاگ‌گیری برای مشاهده خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام! من دستیار هوش مصنوعی شما هستم. فعلاً در حال توسعه می‌باشم."
    )

import ollama
from woocommerce_api import create_product_draft
from competitor_analysis import run_analysis

async def analyze_competitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور شروع تحلیل رقبا.
    """
    await update.message.reply_text("شروع فرآیند تحلیل رقبا... این ممکن است چند دقیقه طول بکشد.")

    try:
        results = run_analysis()

        # فرمت‌بندی نتایج برای نمایش در تلگرام
        response_text = "📊 **نتایج اولیه تحلیل رقبا** 📊\n\n"

        response_text += "🌐 **وب‌سایت‌ها:**\n"
        for site in results.get('websites', []):
            response_text += f"- {site['url']}: *{site['title']}*\n"

        response_text += "\n📱 **اینستاگرام:**\n"
        for profile in results.get('instagrams', []):
            response_text += f"- @{profile['username']} ({profile['followers']} دنبال‌کننده)\n"

        # ارسال نتایج به Llama3 برای دریافت پیشنهاد
        await update.message.reply_text("داده‌ها جمع‌آوری شد. در حال ارسال به مدل هوش مصنوعی برای دریافت پیشنهاد...")

        prompt = f"""
        من یک فروشگاه لوازم تحریر آنلاین به نام 'تحریرچی شاپ' دارم.
        اطلاعات زیر از رقبای من جمع‌آوری شده است:
        {results}

        بر اساس این داده‌ها، یک پیشنهاد اولیه و کلی برای بهبود وضعیت کسب‌وکار من ارائه بده.
        """

        ollama_response = ollama.chat(model='llama3:latest', messages=[{'role': 'user', 'content': prompt}])
        suggestion = ollama_response['message']['content']

        final_response = response_text + "\n\n💡 **پیشنهاد هوش مصنوعی:**\n" + suggestion

        await update.message.reply_text(final_response, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in analyze_competitors_command: {e}")
        await update.message.reply_text("متاسفانه در فرآیند تحلیل خطایی رخ داد.")


async def add_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    دستور افزودن محصول به صورت پیش‌نویس در ووکامرس.
    فرمت: /addproduct نام محصول; قیمت; توضیحات
    """
    try:
        # جدا کردن آرگومان‌ها از دستور
        parts = ' '.join(context.args).split(';')
        if len(parts) < 3:
            await update.message.reply_text(
                "لطفاً از فرمت صحیح استفاده کنید:\n"
                "/addproduct نام محصول; قیمت; توضیحات"
            )
            return

        name = parts[0].strip()
        price = parts[1].strip()
        description = parts[2].strip()

        product_data = {
            'name': name,
            'type': 'simple',
            'regular_price': price,
            'description': description,
            # 'status': 'draft' # این مورد در خود تابع API تنظیم می‌شود
        }

        await update.message.reply_text("در حال ایجاد پیش‌نویس محصول... لطفاً صبر کنید.")

        result = create_product_draft(product_data)

        if result["success"]:
            response_text = f"{result['message']}\n\n"
            response_text += "برای بازبینی و انتشار، روی لینک زیر کلیک کنید:\n"
            response_text += result['edit_link']
        else:
            response_text = f"خطا در ایجاد محصول: {result['message']}"

        await update.message.reply_text(response_text)

    except Exception as e:
        logging.error(f"Error in add_product_command: {e}")
        await update.message.reply_text("متاسفانه در پردازش درخواست شما خطایی رخ داد.")


async def llm_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ هوشمند با استفاده از Llama 3"""
    user_message = update.message.text
    try:
        # ارسال پیام به مدل Llama 3
        response = ollama.chat(model='llama3:latest', messages=[
            {
                'role': 'user',
                'content': user_message,
            },
        ])
        ai_response = response['message']['content']
    except Exception as e:
        logging.error(f"Error communicating with Ollama: {e}")
        ai_response = "متاسفانه در ارتباط با مدل هوش مصنوعی خطایی رخ داد."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ai_response
    )

if __name__ == '__main__':
    # ساخت اپلیکیشن ربات
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # تعریف دستورات
    start_handler = CommandHandler('start', start)
    add_product_handler = CommandHandler('addproduct', add_product_command)
    analyze_handler = CommandHandler('analyze', analyze_competitors_command)
    llm_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), llm_response)

    # افزودن دستورات به اپلیکیشن
    application.add_handler(start_handler)
    application.add_handler(add_product_handler)
    application.add_handler(analyze_handler)
    application.add_handler(llm_handler)

    print("ربات در حال اجراست و به Ollama متصل شده است...")
    # اجرای ربات
    application.run_polling()
