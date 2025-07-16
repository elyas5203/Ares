# dashboard.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>داشبورد مدیریتی دستیار هوش مصنوعی</h1><p>اینجا مرکز کنترل آینده شما خواهد بود.</p>"

if __name__ == '__main__':
    # شما می‌توانید با اجرای دستور python dashboard.py این سرور را راه‌اندازی کنید.
    # سپس در مرورگر خود به آدرس http://127.0.0.1:5000 بروید.
    app.run(debug=True, port=5000)
