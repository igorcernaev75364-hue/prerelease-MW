from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import json
import tempfile
from datetime import datetime
import uuid


def load_dotenv_file(dotenv_path=".env"):
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as dotenv_file:
        for raw_line in dotenv_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv_file()

app = Flask(__name__)

YANDEX_MAPS_API_KEY = os.environ.get("YANDEX_MAPS_API_KEY", "").strip()
YANDEX_MAPS_SUGGEST_API_KEY = os.environ.get("YANDEX_MAPS_SUGGEST_API_KEY", "").strip()
DEFAULT_DELIVERY_CITY = "Москва"
DEFAULT_MAP_CENTER = [37.6176, 55.7558]

# Настройки для Render
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(tempfile.gettempdir(), "mw_store_flask_session")

# Создаём папку для сессий
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

# Настройки для загрузки файлов
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаём папки для данных
ORDERS_DIR = "orders"
if not os.path.exists(ORDERS_DIR):
    os.makedirs(ORDERS_DIR)

# Инициализируем Session
Session(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

products = [
    # ===== ФУТБОЛКИ =====
    {
        "id": 1,
        "title": "Черная футболка",
        "price": 1299,
        "category": "tshirts",
        "category_name": "Футболки",
        "main_image": "tshirt-black.jpg",
        "model_image": None,
        "description": "Классическая черная футболка из 100% хлопка. Идеально подходит для повседневной носки.",
        "features": ["Материал: Хлопок 100%", "Сезон: Всесезонная", "Уход: Машинная стирка"]
    },
    {
        "id": 4,
        "title": "Белая футболка",
        "price": 1299,
        "category": "tshirts",
        "category_name": "Футболки",
        "main_image": "tshirt-white.jpg",
        "model_image": None,
        "description": "Классическая белая футболка из 100% хлопка. Базовый предмет гардероба.",
        "features": ["Материал: Хлопок 100%", "Сезон: Всесезонная", "Уход: Машинная стирка"]
    },
    {
        "id": 5,
        "title": "Серая футболка с принтом",
        "price": 1499,
        "category": "tshirts",
        "category_name": "Футболки",
        "main_image": "tshirt-gray.jpg",
        "model_image": None,
        "description": "Серая футболка с минималистичным принтом логотипа MW STORE.",
        "features": ["Материал: Хлопок 100%", "Принт: Шелкография", "Уход: Стирка при 30°C"]
    },

    # ===== ХУДИ =====
    {
        "id": 3,
        "title": "Худи MW STORE",
        "price": 2599,
        "category": "hoodies",
        "category_name": "Худи",
        "main_image": "hoodie-main.jpg",
        "model_image": "hoodie-model.jpg",
        "description": "Теплое худи с капюшоном и передним карманом. Состав: 80% хлопок, 20% полиэстер.",
        "features": ["Материал: Хлопок 80%, Полиэстер 20%", "Капюшон: Есть", "Карманы: Кенгуру"]
    },
    {
        "id": 6,
        "title": "Худи оверсайз",
        "price": 2999,
        "category": "hoodies",
        "category_name": "Худи",
        "main_image": "hoodie-oversize.jpg",
        "model_image": None,
        "description": "Модное худи оверсайз кроя. Объемный капюшон и широкие рукава.",
        "features": ["Материал: Хлопок 85%, Полиэстер 15%", "Крой: Оверсайз", "Карманы: Боковые"]
    },
    {
        "id": 7,
        "title": "Худи на молнии",
        "price": 2799,
        "category": "hoodies",
        "category_name": "Худи",
        "main_image": "hoodie-zip.jpg",
        "model_image": None,
        "description": "Удобное худи на молнии. Идеально для спорта и повседневной носки.",
        "features": ["Материал: Хлопок 70%, Полиэстер 30%", "Застежка: Молния", "Карманы: 2 боковых"]
    },

    # ===== КРУЖКИ =====
    {
        "id": 2,
        "title": "Белая кружка",
        "price": 799,
        "category": "mugs",
        "category_name": "Кружки",
        "main_image": "mug-white.jpg",
        "model_image": None,
        "description": "Белая керамическая кружка объемом 350 мл. Можно мыть в посудомоечной машине.",
        "features": ["Объем: 350 мл", "Материал: Керамика", "Можно мыть в ПММ"]
    },
    {
        "id": 8,
        "title": "Черная кружка",
        "price": 799,
        "category": "mugs",
        "category_name": "Кружки",
        "main_image": "mug-black.jpg",
        "model_image": None,
        "description": "Стильная черная кружка с золотым принтом логотипа.",
        "features": ["Объем: 350 мл", "Материал: Керамика", "Принт: Золотая фольга"]
    },
    {
        "id": 9,
        "title": "Кружка с принтом",
        "price": 899,
        "category": "mugs",
        "category_name": "Кружки",
        "main_image": "mug-print.jpg",
        "model_image": None,
        "description": "Кружка с фирменным принтом MW STORE. Объем 400 мл.",
        "features": ["Объем: 400 мл", "Материал: Керамика", "Принт: Полноцветный"]
    },

    # ===== АКСЕССУАРЫ =====
    {
        "id": 10,
        "title": "Бейсболка MW",
        "price": 1299,
        "category": "accessories",
        "category_name": "Аксессуары",
        "main_image": "cap.jpg",
        "model_image": None,
        "description": "Хлопковая бейсболка с вышитым логотипом. Регулируемый размер.",
        "features": ["Материал: Хлопок 100%", "Размер: Регулируемый", "Козырек: Изогнутый"]
    },
    {
        "id": 11,
        "title": "Шоппер MW",
        "price": 999,
        "category": "accessories",
        "category_name": "Аксессуары",
        "main_image": "bag.jpg",
        "model_image": None,
        "description": "Экологичная сумка-шоппер из плотного хлопка. Вместительная и прочная.",
        "features": ["Материал: Хлопок 100%", "Размер: 40x35 см", "Ручки: Длинные"]
    },
    {
        "id": 12,
        "title": "Носки MW",
        "price": 499,
        "category": "accessories",
        "category_name": "Аксессуары",
        "main_image": "socks.jpg",
        "model_image": None,
        "description": "Уютные носки с логотипом. Состав: хлопок, полиэстер, эластан.",
        "features": ["Размер: 39-43", "Состав: Хлопок 80%", "Упаковка: Пара"]
    },

    # ===== ТОЛСТОВКИ =====
    {
        "id": 13,
        "title": "Толстовка MW",
        "price": 2199,
        "category": "sweatshirts",
        "category_name": "Толстовки",
        "main_image": "sweatshirt.jpg",
        "model_image": None,
        "description": "Теплая толстовка с круглым вырезом и принтом на груди.",
        "features": ["Материал: Хлопок 80%", "Капюшон: Нет", "Карман: Кенгуру"]
    },
    {
        "id": 14,
        "title": "Толстовка лапша",
        "price": 2399,
        "category": "sweatshirts",
        "category_name": "Толстовки",
        "main_image": "sweatshirt-ribbed.jpg",
        "model_image": None,
        "description": "Толстовка с фактурной вязкой 'лапша'. Очень теплая и уютная.",
        "features": ["Материал: Акрил 100%", "Фактура: Ребристая", "Крой: Прямой"]
    },
]


def calculate_total(cart):
    total = 0
    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            total += qty * product["price"]
    return total


VALID_CATEGORIES = {"tshirts", "hoodies", "sweatshirts", "mugs", "accessories"}
VALID_PRICE_RANGES = {"all", "0-1000", "1000-2000", "2000+"}
VALID_SORT_OPTIONS = {"default", "price_asc", "price_desc", "name"}


def normalize_catalog_filters(category, price_range, sort_by):
    category = category if category in VALID_CATEGORIES else None
    price_range = price_range if price_range in VALID_PRICE_RANGES else "all"
    sort_by = sort_by if sort_by in VALID_SORT_OPTIONS else "default"
    return category, price_range, sort_by


def apply_catalog_filters(items, category=None, price_range="all"):
    filtered_items = list(items)

    if category:
        filtered_items = [item for item in filtered_items if item.get("category") == category]

    if price_range == "0-1000":
        filtered_items = [item for item in filtered_items if item["price"] <= 1000]
    elif price_range == "1000-2000":
        filtered_items = [item for item in filtered_items if 1000 <= item["price"] <= 2000]
    elif price_range == "2000+":
        filtered_items = [item for item in filtered_items if item["price"] >= 2000]

    return filtered_items


def sort_catalog_products(items, sort_by="default"):
    sorted_items = list(items)

    if sort_by == "price_asc":
        sorted_items.sort(key=lambda item: item["price"])
    elif sort_by == "price_desc":
        sorted_items.sort(key=lambda item: item["price"], reverse=True)
    elif sort_by == "name":
        sorted_items.sort(key=lambda item: item["title"])

    return sorted_items


def build_products_url(category=None, price_range="all", sort_by="default"):
    params = {}
    if category:
        params["category"] = category
    if price_range != "all":
        params["price"] = price_range
    if sort_by != "default":
        params["sort"] = sort_by
    return url_for("products_page", **params)


def save_order_to_txt(order_data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write(f"ЗАКАЗ #{order_data['order_id']}\n")
        f.write(f"Дата: {order_data['timestamp']}\n")
        f.write("=" * 50 + "\n\n")
        f.write("👤 ПОКУПАТЕЛЬ:\n")
        f.write(f"  Имя: {order_data['customer']['name']}\n")
        f.write(f"  Телефон: {order_data['customer']['phone']}\n")
        f.write(f"  Email: {order_data['customer']['email']}\n")
        f.write(f"  Адрес доставки: {order_data['customer'].get('delivery_address', 'Не указан')}\n\n")
        f.write("💳 ОПЛАТА:\n")
        payment_names = {'card': 'Банковская карта', 'sbp': 'СБП', 'cash': 'Наличные'}
        f.write(f"  Способ: {payment_names.get(order_data['payment_method'], order_data['payment_method'])}\n\n")
        f.write("📦 ТОВАРЫ:\n")
        for item in order_data['cart_items']:
            f.write(f"  • {item['title']} - {item['price']}₽ × {item['qty']} = {item['subtotal']}₽\n")
        f.write("\n" + "-" * 50 + "\n")
        f.write(f"ИТОГО: {order_data['total']}₽\n")
        f.write("=" * 50 + "\n")


# ===== ОСНОВНЫЕ МАРШРУТЫ =====
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def products_page():
    category, price_range, sort_by = normalize_catalog_filters(
        request.args.get("category"),
        request.args.get("price", "all"),
        request.args.get("sort", "default"),
    )

    filtered_products = sort_catalog_products(
        apply_catalog_filters(products, category=category, price_range=price_range),
        sort_by=sort_by,
    )

    products_for_category_counts = apply_catalog_filters(products, price_range=price_range)
    category_counts = {
        "all": len(products_for_category_counts),
        "tshirts": len([item for item in products_for_category_counts if item["category"] == "tshirts"]),
        "hoodies": len([item for item in products_for_category_counts if item["category"] == "hoodies"]),
        "sweatshirts": len([item for item in products_for_category_counts if item["category"] == "sweatshirts"]),
        "mugs": len([item for item in products_for_category_counts if item["category"] == "mugs"]),
        "accessories": len([item for item in products_for_category_counts if item["category"] == "accessories"]),
    }

    return render_template("products.html",
                           products=filtered_products,
                           current_category=category,
                           current_price=price_range,
                           current_sort=sort_by,
                           category_counts=category_counts,
                           all_products_url=build_products_url(price_range=price_range, sort_by=sort_by),
                           category_urls={
                               "tshirts": build_products_url("tshirts", price_range=price_range, sort_by=sort_by),
                               "hoodies": build_products_url("hoodies", price_range=price_range, sort_by=sort_by),
                               "sweatshirts": build_products_url("sweatshirts", price_range=price_range, sort_by=sort_by),
                               "mugs": build_products_url("mugs", price_range=price_range, sort_by=sort_by),
                               "accessories": build_products_url("accessories", price_range=price_range, sort_by=sort_by),
                           })


@app.route("/product/<int:pid>")
def product_detail(pid):
    product = next((p for p in products if p["id"] == pid), None)
    if not product:
        return redirect(url_for("products_page"))
    return render_template("product.html", product=product)


# ===== МАРШРУТЫ КОРЗИНЫ =====

@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    cart_products = []
    total = 0

    for pid, qty in cart_data.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            cart_item = {
                "id": product["id"],
                "title": product["title"],
                "price": product["price"],
                "qty": qty,
                "subtotal": qty * product["price"],
                "main_image": product.get("main_image", None)
            }
            cart_products.append(cart_item)
            total += cart_item["subtotal"]

    return render_template("cart.html", cart=cart_products, total=total)


@app.route("/api/cart")
def cart_api():
    """API endpoint для обновления виджета корзины"""
    cart_data = session.get("cart", {})
    cart_products = []
    total = 0

    for pid, qty in cart_data.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            cart_products.append({
                "id": pid,
                "title": product["title"],
                "price": product["price"],
                "qty": qty,
                "subtotal": qty * product["price"],
                "image": product.get("main_image", None)
            })
            total += qty * product["price"]

    return jsonify({
        "cart": cart_products,
        "total": total
    })


@app.route("/add_to_cart/<int:pid>", methods=["POST"])
def add_to_cart(pid):
    cart = session.get("cart", {})
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart

    # Если запрос через AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "ok", "cart": cart})

    # Иначе редирект (для форм без JS)
    return redirect(request.referrer or url_for("products_page"))


@app.route("/update_cart/<int:pid>", methods=["POST"])
def update_cart(pid):
    """Обновление количества товара через форму (для страницы корзины)"""
    action = request.form.get("action")
    cart = session.get("cart", {})

    if pid in cart:
        if action == "increase":
            cart[pid] = cart[pid] + 1
        elif action == "decrease":
            cart[pid] = cart[pid] - 1
            if cart[pid] <= 0:
                del cart[pid]
        elif action == "remove":
            del cart[pid]

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/api/update_cart/<int:pid>", methods=["POST"])
def api_update_cart(pid):
    """API endpoint для обновления количества товара (для мини-корзины)"""
    data = request.get_json()
    change = data.get('change', 0)

    cart = session.get("cart", {})

    if pid in cart:
        cart[pid] = cart[pid] + change
        if cart[pid] <= 0:
            del cart[pid]
    elif change > 0:
        cart[pid] = change

    session["cart"] = cart
    return jsonify({"status": "ok", "cart": cart})


@app.route("/api/remove_from_cart/<int:pid>", methods=["POST"])
def api_remove_from_cart(pid):
    """API endpoint для удаления товара (для мини-корзины)"""
    cart = session.get("cart", {})

    if pid in cart:
        del cart[pid]

    session["cart"] = cart
    return jsonify({"status": "ok", "cart": cart})


@app.route("/remove_from_cart/<int:pid>", methods=["POST"])
def remove_from_cart(pid):
    """Удаление товара через форму (для страницы корзины)"""
    cart = session.get("cart", {})

    if pid in cart:
        del cart[pid]

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():
    cart_data = session.get("cart", {})
    if not cart_data:
        return redirect(url_for("cart"))

    cart_products = []
    total = 0
    for pid, qty in cart_data.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            cart_item = {
                "id": product["id"],
                "title": product["title"],
                "price": product["price"],
                "qty": qty,
                "subtotal": qty * product["price"],
                "main_image": product.get("main_image", None)
            }
            cart_products.append(cart_item)
            total += cart_item["subtotal"]

    return render_template(
        "checkout.html",
        cart=cart_products,
        total=total,
        yandex_maps_api_key=YANDEX_MAPS_API_KEY,
        yandex_maps_suggest_api_key=YANDEX_MAPS_SUGGEST_API_KEY,
        default_delivery_city=DEFAULT_DELIVERY_CITY,
        default_map_center=DEFAULT_MAP_CENTER,
    )


@app.route("/place_order", methods=["POST"])
def place_order():
    try:
        order_data = {
            "order_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer": {
                "name": request.form.get("name"),
                "phone": request.form.get("phone"),
                "email": request.form.get("email"),
                "delivery_address": request.form.get("delivery_address")  # Добавляем адрес доставки
            },
            "payment_method": request.form.get("payment"),
            "cart": session.get("cart", {}),
            "total": calculate_total(session.get("cart", {}))
        }
        cart_items = []
        for pid, qty in order_data["cart"].items():
            product = next((p for p in products if p["id"] == int(pid)), None)
            if product:
                cart_items.append({
                    "id": pid,
                    "title": product["title"],
                    "price": product["price"],
                    "qty": qty,
                    "subtotal": qty * product["price"]
                })

        order_data["cart_items"] = cart_items

        json_filename = f"{ORDERS_DIR}/order_{order_data['order_id']}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, ensure_ascii=False, indent=2)

        txt_filename = f"{ORDERS_DIR}/order_{order_data['order_id']}.txt"
        save_order_to_txt(order_data, txt_filename)

        session["cart"] = {}
        return render_template("order_success.html", order_id=order_data["order_id"])

    except Exception as e:
        return render_template("checkout.html", error=str(e))


@app.route("/admin/upload/<int:product_id>", methods=["GET", "POST"])
def admin_upload(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "Товар не найден", 404

    if request.method == "POST":
        if 'photo' not in request.files:
            return "Файл не выбран", 400

        file = request.files['photo']

        if file.filename == '':
            return "Файл не выбран", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = f"{product_id}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(filepath)

            return f"""
            <div style="text-align: center; padding: 50px; background: #000; color: #fff;">
                <h2>✅ Фото загружено!</h2>
                <p>Файл сохранён как: <code>{new_filename}</code></p>
                <p>Теперь укажите в товаре <code>main_image: "{new_filename}"</code></p>
                <a href="/admin/upload/{product_id}" style="color: #ffd700;">Загрузить ещё</a><br>
                <a href="/products" style="color: #4cd964;">Вернуться в каталог</a>
            </div>
            """
        else:
            return "Неподдерживаемый формат файла. Используйте PNG, JPG, JPEG, GIF, WEBP", 400

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Загрузка фото для {product['title']}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: system-ui, sans-serif; background: #000; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
            .container {{ background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 32px; padding: 40px; max-width: 500px; width: 100%; text-align: center; border: 1px solid rgba(255,255,255,0.1); }}
            h1 {{ font-size: 1.8rem; margin-bottom: 10px; }}
            .product-name {{ color: #aaa; margin-bottom: 30px; }}
            .current-photo {{ background: rgba(255,255,255,0.03); border-radius: 20px; padding: 20px; margin: 20px 0; }}
            .current-photo img {{ max-width: 200px; border-radius: 16px; }}
            .upload-area {{ border: 2px dashed rgba(255,255,255,0.3); border-radius: 24px; padding: 40px; margin: 20px 0; cursor: pointer; transition: all 0.3s; }}
            .upload-area:hover {{ border-color: #ffd700; background: rgba(255,215,0,0.05); }}
            input[type="file"] {{ display: none; }}
            button {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 40px; padding: 12px 30px; color: white; font-size: 1rem; cursor: pointer; transition: all 0.3s; margin-top: 20px; }}
            button:hover {{ background: rgba(255,255,255,0.2); transform: translateY(-2px); }}
            .back-link {{ display: inline-block; margin-top: 20px; color: #aaa; text-decoration: none; }}
            .hint {{ font-size: 0.8rem; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📸 Загрузка фото</h1>
            <div class="product-name">Товар: <strong>{product['title']}</strong> (ID: {product_id})</div>

            <div class="current-photo">
                <p>Текущее фото:</p>
                <img src="/static/images/products/{product.get('main_image', 'no-image.jpg')}" 
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22 viewBox=%220 0 100 100%22%3E%3Crect width=%22100%22 height=%22100%22 fill=%22%23333%22/%3E%3Ctext x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23666%22%3EНет фото%3C/text%3E%3C/svg%3E'"
                     style="max-width: 150px; border-radius: 12px;">
                <p style="font-size: 0.8rem; margin-top: 10px;">Файл: {product.get('main_image', 'не задан')}</p>
            </div>

            <form method="POST" enctype="multipart/form-data" id="uploadForm">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <div style="font-size: 48px; margin-bottom: 10px;">📤</div>
                    <p>Нажмите или перетащите файл</p>
                    <p style="font-size: 0.7rem; color: #666;">PNG, JPG, JPEG, GIF, WEBP до 16MB</p>
                </div>
                <input type="file" name="photo" id="fileInput" accept="image/*" onchange="document.getElementById('uploadForm').submit()">
                <button type="submit">Загрузить фото</button>
            </form>

            <a href="/products" class="back-link">← Вернуться в каталог</a>
            <div class="hint">
                💡 После загрузки обновите main_image в app.py на имя загруженного файла
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/admin/products")
def admin_products():
    products_html = ""
    for p in products:
        icon = "👕" if p['category'] == 'tshirts' else "🧥" if p['category'] == 'hoodies' else "☕" if p['category'] == 'mugs' else "🎒"
        products_html += f"""
        <div class="product-item">
            <div class="product-info">
                <div class="product-icon">{icon}</div>
                <div>
                    <div class="product-title">{p['title']}</div>
                    <div class="product-category">{p.get('category_name', p['category'])} • {p['price']}₽</div>
                </div>
            </div>
            <a href="/admin/upload/{p['id']}" class="upload-btn">📤 Загрузить фото</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Управление фото товаров</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: system-ui, sans-serif; background: #000; color: #fff; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ text-align: center; margin-bottom: 30px; }}
            .product-list {{ display: flex; flex-direction: column; gap: 12px; }}
            .product-item {{ background: rgba(255,255,255,0.05); backdrop-filter: blur(5px); border-radius: 20px; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; border: 1px solid rgba(255,255,255,0.1); transition: all 0.3s; }}
            .product-item:hover {{ background: rgba(255,255,255,0.08); transform: translateX(5px); }}
            .product-info {{ display: flex; align-items: center; gap: 15px; }}
            .product-icon {{ width: 50px; height: 50px; background: rgba(255,255,255,0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }}
            .product-title {{ font-weight: 600; }}
            .product-category {{ font-size: 0.8rem; color: #aaa; }}
            .upload-btn {{ background: rgba(255,215,0,0.2); border: 1px solid rgba(255,215,0,0.3); border-radius: 30px; padding: 8px 20px; color: #ffd700; text-decoration: none; transition: all 0.3s; }}
            .upload-btn:hover {{ background: rgba(255,215,0,0.3); transform: translateY(-2px); }}
            .back-link {{ display: block; text-align: center; margin-top: 30px; color: #aaa; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📸 Управление фото товаров</h1>
            <div class="product-list">
                {products_html}
            </div>
            <a href="/products" class="back-link">← Вернуться в каталог</a>
        </div>
    </body>
    </html>
    """


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
