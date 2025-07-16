# product_manager.py

from woocommerce_api import upload_image_to_wordpress, create_product_draft, get_product_categories
import os
import ollama
import json

def get_smart_category(product_name: str, categories: list):
    """
    با استفاده از Llama 3، بهترین دسته‌بندی را برای محصول انتخاب می‌کند.
    """
    if not categories:
        return None

    # ساخت لیست نام دسته‌بندی‌ها برای ارسال به مدل
    category_names = [cat['name'] for cat in categories]

    prompt = f"""
    You are an expert AI for an online stationery shop.
    Your task is to categorize a new product.
    Product Name: "{product_name}"
    Available Categories: {category_names}

    Based on the product name, which is the single most appropriate category from the list?
    Respond with the category name only, exactly as it appears in the list.
    For example, if the best category is "Pens", your response should be just "Pens".
    """

    try:
        response = ollama.chat(
            model='llama3:latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        chosen_category_name = response['message']['content'].strip()

        # پیدا کردن شناسه دسته‌بندی انتخاب شده
        for cat in categories:
            if cat['name'] == chosen_category_name:
                print(f"مدل هوش مصنوعی دسته‌بندی '{chosen_category_name}' را انتخاب کرد.")
                return cat['id']

        print(f"هشدار: مدل دسته‌بندی '{chosen_category_name}' را انتخاب کرد که در لیست موجود نیست.")
        return None

    except Exception as e:
        print(f"خطا در ارتباط با Ollama برای انتخاب دسته‌بندی: {e}")
        return None


def generate_product_description(product_name: str):
    """
    با استفاده از Llama 3، توضیحات محصول را تولید می‌کند.
    """
    prompt = f"""
    You are a creative copywriter for an online stationery shop called "Tahrirchi Shop".
    Your task is to write a compelling and friendly product description for a new item.

    Product Name: "{product_name}"

    Write a short, engaging description (around 2-3 sentences).
    Highlight its potential use or a key feature.
    Keep the tone friendly and appealing to students, artists, and office workers.
    Do not use placeholders like "[Product Name]". Instead, use the actual name.
    """
    try:
        response = ollama.chat(
            model='llama3:latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        description = response['message']['content'].strip()
        print(f"مدل هوش مصنوعی توضیحات زیر را تولید کرد:\n---\n{description}\n---")
        return description
    except Exception as e:
        print(f"خطا در ارتباط با Ollama برای تولید توضیحات: {e}")
        return f"توضیحات محصول {product_name}" # بازگرداندن یک متن پیش‌فرض در صورت خطا


def handle_new_product_submission(local_image_path: str, product_name: str):
    """
    فرآیند کامل و هوشمند ثبت یک محصول جدید را مدیریت می‌کند.
    """
    # مرحله ۱: آپلود عکس
    print("مرحله ۱: در حال آپلود تصویر به وردپرس...")
    image_id, upload_message = upload_image_to_wordpress(local_image_path, product_name)
    if not image_id:
        return {"success": False, "message": f"آپلود عکس ناموفق بود. خطا: {upload_message}", "edit_link": None}
    print(f"آپلود عکس موفقیت‌آمیز بود. شناسه عکس: {image_id}")

    # مرحله ۲: دریافت دسته‌بندی‌ها از سایت
    print("مرحله ۲: در حال دریافت دسته‌بندی‌ها از ووکامرس...")
    categories = get_product_categories()

    # مرحله ۳: انتخاب هوشمند دسته‌بندی
    category_id = None
    if categories:
        print("مرحله ۳: در حال انتخاب هوشمند دسته‌بندی...")
        category_id = get_smart_category(product_name, categories)

    # مرحله ۴: تولید خودکار توضیحات
    print("مرحله ۴: در حال تولید خودکار توضیحات محصول...")
    description = generate_product_description(product_name)

    # مرحله ۵: آماده‌سازی و ایجاد پیش‌نویس محصول
    print("مرحله ۵: در حال ایجاد پیش‌نویس محصول در ووکامرس...")
    product_data = {
        'name': product_name,
        'type': 'simple',
        'status': 'draft',
        'description': description,
        'images': [{'id': image_id}]
    }
    if category_id:
        product_data['categories'] = [{'id': category_id}]

    result = create_product_draft(product_data)

    # پاک کردن فایل موقت
    try:
        os.remove(local_image_path)
        print(f"فایل موقت '{local_image_path}' با موفقیت پاک شد.")
    except OSError as e:
        print(f"خطا در پاک کردن فایل موقت: {e}")

    return result
