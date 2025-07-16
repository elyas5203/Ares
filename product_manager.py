# product_manager.py

from woocommerce_api import upload_image_to_wordpress, create_product_draft, get_product_categories
import os
import ollama
import json



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


def handle_new_product_submission(local_image_path: str = None, product_name: str, category_id: int = None, category_name: str = None, description: str = None, price: str = None):
    """
    فرآیند کامل ثبت یک محصول جدید را مدیریت می‌کند.
    می‌تواند با عکس یا بدون عکس، و با دسته‌بندی دستی یا انتخابی کار کند.
    """
    image_id = None
    if local_image_path:
        # مرحله ۱ (در صورت وجود عکس): آپلود عکس
        print(f"مرحله ۱: در حال آپلود تصویر برای محصول «{product_name}»...")
        image_id, upload_message = upload_image_to_wordpress(local_image_path, product_name)
        if not image_id:
            return {"success": False, "message": f"آپلود عکس ناموفق بود. خطا: {upload_message}", "edit_link": None}
        print(f"آپلود موفقیت‌آمیز بود. شناسه عکس: {image_id}")

    # مرحله ۲: تعیین توضیحات
    if not description:
        # اگر توضیحات به صورت دستی ارائه نشده بود، آن را تولید کن
        print("مرحله ۲: در حال تولید خودکار توضیحات محصول...")
        description = generate_product_description(product_name)
    else:
        print("مرحله ۲: استفاده از توضیحات دستی ارائه شده.")

    # مرحله ۳: تعیین دسته‌بندی
    final_category_id = category_id
    if category_name and not final_category_id:
        print(f"مرحله ۳: در حال جستجو برای دسته‌بندی متنی: '{category_name}'")
        categories = get_product_categories()
        for cat in categories:
            if cat['name'].lower() == category_name.lower():
                final_category_id = cat['id']
                print(f"دسته‌بندی متنی '{category_name}' با شناسه {final_category_id} یافت شد.")
                break

    # مرحله ۴: آماده‌سازی و ایجاد پیش‌نویس محصول
    print(f"مرحله ۴: در حال ایجاد پیش‌نویس با دسته‌بندی ID: {final_category_id}...")
    product_data = {
        'name': product_name,
        'type': 'simple',
        'status': 'draft',
        'description': description,
    }
    if price:
        product_data['regular_price'] = price
    if image_id:
        product_data['images'] = [{'id': image_id}]
    if final_category_id:
        product_data['categories'] = [{'id': final_category_id}]

    result = create_product_draft(product_data)

    # پاک کردن فایل موقت در صورت وجود
    if local_image_path:
        try:
            os.remove(local_image_path)
            print(f"فایل موقت '{local_image_path}' با موفقیت پاک شد.")
        except OSError as e:
            print(f"خطا در پاک کردن فایل موقت: {e}")

    return result
