import datetime
from json import dumps

from flask import abort, Flask, redirect, render_template, request, session
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
from flask_socketio import join_room, leave_room, send, SocketIO
from PIL import Image
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import or_
from static.python.functions import fill_db
from translate import Translator
import asyncio

from data import db_session
from data.categories import Category
from data.comments import Comment
from data.criterias import Criteria
from data.dish_categories import DishCategory
from data.dish_lunch_orders import DishLunchOrder
from data.dish_orders import DishOrder
from data.dishes import Dish
from data.dishes_lunch import DishLunch
from data.lunch_orders import LunchOrder
from data.lunches import Lunch
from data.messages import Message
from data.normalized_categories import NormalizedCategory
from data.orders import Order
from data.posts import Post
from data.stats import Stat
from data.users import User
from data.valuations import Valuation
from data.votes import Vote
from forms.category import CategoryForm
from forms.comment import CommentForm
from forms.criteria import CriteriaForm
from forms.dish import DishForm
from forms.login import LoginForm
from forms.lunch import LunchForm
from forms.normalized_category import NormalizedCategoryForm
from forms.post import PostForm
from forms.stat import StatForm
from forms.user import UserForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secret_key"
socketio = SocketIO(app)

ST_message = {"status": 404, "text": ""}
STATUS = {1: "В процессе", 2: "Приготовлен", 3: "Выдан", 4: "Передан в доставку", 5: "Доставлен", 0: "Отменён"}

login_manager = LoginManager()
login_manager.init_app(app)

api_url = "https://api.calorieninjas.com/v1/nutrition?query="


@app.route("/")
def index():
    if not session.get("message"):
        session["message"] = dumps(ST_message)
    if not session.get("order"):
        session["order"] = {}
    if current_user.is_authenticated:
        if current_user.role == 1:
            return redirect("/orders")
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).join(DishCategory).all()
    posts = db_sess.query(Post).order_by(Post.date).all()[::-1][0:3]
    lunch = db_sess.query(Lunch).filter(Lunch.date == datetime.date.today()).first()

    return render_template(
        "index.html",
        title="Добро пожаловать",
        message=smessage,
        order=session["order"],
        categories=categories,
        posts=posts,
        lunch=lunch,
    )


@app.route("/add_dish/<int:dish_id>")
def add_dish(dish_id):
    if current_user.is_authenticated:
        if current_user.role in [0, 1]:
            return redirect("/")
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).get(dish_id)
    if not dish:
        return redirect("/")
    if not session.get("order"):
        session["order"] = {}
    if session["order"].get(str(dish_id)):
        session["order"][str(dish_id)]["count"] += 1
    else:
        d1 = dish.to_dict()
        d1["count"] = 1
        session["order"][str(dish_id)] = d1
    dc = session["order"]
    session["order"]["sum"] = sum(dc[v]["count"] * dc[v]["price"] if v not in ["sum"] else 0 for v in dc)
    session["order"] = session["order"]
    return redirect("/")


@app.route("/cancel_order/<int:order_id>")
def cancel_order(order_id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    order = db_sess.query(Order).get(order_id)
    if not order:
        abort(404)
    if current_user.role == 2 and current_user.id != order.user.id:
        abort(404)
    order.status = 0
    order.edit_date = datetime.date.today()
    db_sess.merge(order)
    db_sess.commit()
    return redirect(f"/orders#{order_id}")


@app.route("/change_order/<int:order_id>")
def change_order(order_id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    order = db_sess.query(Order).get(order_id)
    if not order:
        abort(404)
    if order.status in [0, 3, 5]:
        return redirect(f"/orders#{order_id}")
    if current_user.role == 2:
        abort(404)
    if order.status == 2 and order.is_delivery:
        order.status += 1
    order.status += 1
    order.edit_date = datetime.date.today()
    db_sess.merge(order)
    db_sess.commit()
    return redirect(f"/orders#{order_id}")


@app.route("/confirm_order", methods=["GET", "POST"])
def confirm_order():
    if current_user.is_authenticated:
        if current_user.role in [0, 1]:
            abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    title = "Подтвердите заказ"
    if request.method == "GET":
        return render_template("confirm_order.html", title=title, message=smessage, order=session["order"])
    if request.method == "POST":
        if request.form.get("req_version") == "PC":
            counts = request.form.getlist("rcounts")
        else:
            counts = request.form.getlist("rrcounts")
        to_del = set()
        for i, k in enumerate(session["order"]):
            if k in ["sum", "lunch"]:
                continue
            if int(counts[i]) == 0:
                to_del.add(k)
                continue
            session["order"][k]["count"] = int(counts[i])
        for k in to_del:
            del session["order"][k]
        dc = session["order"]
        session["order"]["sum"] = sum(dc[v]["count"] * dc[v]["price"] if v != "sum" else 0 for v in dc)

        if not current_user.is_authenticated:
            message = {"status": 2, "text": "Для оформления заказа авторизуйтесь"}
            session["message"] = dumps(message)
            return redirect("/login")
        if list(session["order"]) == ["sum"]:
            message = {"status": 0, "text": "Корзина пустая"}
            session["message"] = dumps(message)
            session["order"] = {}
            return redirect("/")
        is_delivery = request.form.get("is_delivery") == "true"
        if is_delivery:
            address = request.form.get("delivery_address")
            if not address:
                message = {"status": 0, "text": "Укажите место доставки"}
                session["message"] = dumps(message)
                return redirect("/confirm_order")
            delivery_time = request.form.get("delivery_time")
            if delivery_time:
                delivery_time = datetime.datetime.strptime(delivery_time, "%H:%M").time()
                now = datetime.datetime.now().time()
                delta = (delivery_time.hour - now.hour) * 60 + (delivery_time.minute - now.minute)
                if delta < 15:
                    message = {"status": 0, "text": "Доставка требует минимум 15 минут"}
                    session["message"] = dumps(message)
                    return redirect("/confirm_order")
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).all()
        last_id = 1 if not orders else orders[-1].id + 1
        order = Order(
            id=last_id,
            user_id=current_user.id,
            status=1,
            price=session["order"]["sum"],
        )
        if is_delivery:
            order.is_delivery = True
            order.delivery_address = address
            if delivery_time:
                order.delivery_time = delivery_time

        db_sess.add(order)
        for k in session["order"]:
            if k == "sum":
                continue
            if k == "lunch":
                order_lunch = session["order"]["lunch"]
                date = datetime.datetime.strptime(order_lunch["date"], "%d.%m.%Y")
                add_lunch = LunchOrder(
                    order=order,
                    lunch_id=order_lunch["id"],
                    price=order_lunch["price"],
                    date=date,
                )
                db_sess.add(add_lunch)
                for di in order_lunch["dishes"]:
                    dish = DishLunchOrder(
                        lunch=add_lunch,
                        dish_id=di["id"],
                        category=di["category"],
                        image=di["image"],
                        title=di["title"],
                    )
                    db_sess.add(dish)
                db_sess.commit()
                continue
            el = session["order"][k]

            dish_order = DishOrder(
                dish_id=int(k),
                order_id=last_id,
                count=el["count"],
                price=el["price"],
            )
            db_sess.add(dish_order)
            if (
                not db_sess.query(Stat)
                .filter(Stat.dish_id == int(k))
                .filter(Stat.date == datetime.date.today())
                .first()
            ):
                stat = Stat(dish_id=int(k), date=datetime.date.today(), count=el["count"])
            else:
                stat = (
                    db_sess.query(Stat)
                    .filter(Stat.dish_id == int(k))
                    .filter(Stat.date == datetime.date.today())
                    .first()
                )
                stat.count += el["count"]
            db_sess.add(stat)
        db_sess.commit()
        message = {"status": 1, "text": "Заказ оформлен"}
        session["message"] = dumps(message)
        session["order"] = {}
    return redirect("/")


@app.route("/create/dish", methods=["GET", "POST"])
def create_dish():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    form = DishForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Создание блюда"
    db_sess = db_session.create_session()
    if not form.main_category.choices:
        normolized_categories = db_sess.query(NormalizedCategory).all()
        form.main_category.choices = [(cat.id, cat.title) for cat in normolized_categories]
    categories = db_sess.query(Category).all()
    if form.validate_on_submit():
        if db_sess.query(Dish).filter(Dish.title == form.title.data).first():
            message = {"status": 0, "text": "Такое блюдо уже есть в меню"}
            return render_template(
                "create_dish.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
                categories=categories,
            )
        query = Translator(from_lang="russian", to_lang="english").translate(form.title.data)
        query = f"{form.mass.data}g " + query
        response = requests.get(api_url + query, headers={"X-Api-Key": "uKs0cNCsySCuE/7uGjOldQ==ve4Drp6e8VJSfX1V"})
        if response.status_code == requests.codes.ok:
            data = response.json()
        if data.get("items"):
            data = data["items"][0]
        else:
            data = {"calories": 0, "protein_g": 0, "fat_total_g": 0, "carbohydrates_total_g": 0}
        dish = Dish(
            title=form.title.data,
            price=form.price.data,
            description=form.description.data.strip(),
            normalized_category_id=form.main_category.data,
            mass=form.mass.data,
            calories=data["calories"],
            protein=data["protein_g"],
            fat=data["fat_total_g"],
            carbo=data["carbohydrates_total_g"],
        )

        dishes = db_sess.query(Dish).all()
        last_id = 1 if not dishes else dishes[-1].id + 1
        categories = request.form.getlist("categories")
        for category in categories:
            d_categ = DishCategory(dish_id=last_id, category_id=category)
            db_sess.add(d_categ)
            db_sess.commit()
        if form.image.data:
            img1 = form.image.data
            img1.save(f"static/img/dishes/{last_id}.jpg")
        else:
            Image.open("static/img/dishes/no-img.jpg").save(f"static/img/dishes/{last_id}.jpg")
        dish.image = f"img/dishes/{last_id}.jpg"
        db_sess.add(dish)
        db_sess.commit()
        return redirect("/dishes")
    return render_template(
        "create_dish.html",
        title=title,
        form=form,
        message=smessage,
        order=session["order"],
        categories=categories,
    )


@app.route("/create/category", methods=["GET", "POST"])
def create_category():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    form = CategoryForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Создание категории"
    db_sess = db_session.create_session()
    if not form.main_category.choices:
        normolized_categories = db_sess.query(NormalizedCategory).all()
        form.main_category.choices = [(cat.id, cat.title) for cat in normolized_categories]
    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.title == form.title.data).first():
            message = {"status": 0, "text": "Категория с таким названием уже есть"}
            return render_template(
                "create_category.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        category = Category(
            title=form.title.data,
            normalized_category_id=form.main_category.data,
        )

        categories = db_sess.query(Category).all()
        last_id = 1 if not categories else categories[-1].id + 1
        if form.image.data:
            img1 = form.image.data
            img1.save(f"static/img/categories/{last_id}.jpg")
        else:
            Image.open("static/img/categories/no-img.jpg").save(f"static/img/categories/{last_id}.jpg")
        category.image = f"img/categories/{last_id}.jpg"
        db_sess.add(category)
        db_sess.commit()
        message = {"status": 1, "text": "Категория создана"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template("create_category.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/delete/category/<int:categ_id>")
def delete_category(categ_id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == categ_id).first()
    if not category:
        abort(404)
    db_sess.delete(category)
    db_sess.commit()
    return redirect("/")


@app.route("/delete/dish/<int:dish_id>")
def delete_dish(dish_id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        abort(404)
    dish_orders = db_sess.query(DishOrder).filter(DishOrder.dish_id == dish_id).all()
    for di_o in dish_orders:
        order = di_o.order
        order.status = 0
        db_sess.merge(di_o)
        db_sess.merge(order)
    db_sess.delete(dish)
    db_sess.commit()
    return redirect("/dishes")


@app.route("/dishes")
def dishes():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    dishes = db_sess.query(Dish).all()
    return render_template("dish_list.html", message=smessage, order=session["order"], dishes=dishes)


@app.route("/register/user", methods=["GET", "POST"])
def register_user():
    if current_user.is_authenticated:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    form = UserForm()
    title = "Регистрация"
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            message = {"status": 0, "text": "Пароли не совпадают"}
            return render_template(
                "register_user.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            message = {"status": 0, "text": "Такой пользователь уже есть"}
            return render_template(
                "register_user.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            role=2,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        login_user(user, remember=False)
        message = {"status": 1, "text": "Успешная авторизация"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template("register_user.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/register/spec", methods=["GET", "POST"])
def register_spec():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    form = UserForm()
    title = "Регистрация"
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            message = {"status": 0, "text": "Пароли не совпадают"}
            return render_template(
                "register_spec.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            message = {"status": 0, "text": "Такой пользователь уже есть"}
            return render_template(
                "register_spec.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        user = User(
            email=form.email.data,
            role=1,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        message = {"status": 1, "text": "Специалист создан"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template("register_spec.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/edit/category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == category_id).first()
    if not category:
        abort(404)
    form = CategoryForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Изменение категории"
    if not form.main_category.choices:
        normolized_categories = db_sess.query(NormalizedCategory).all()
        form.main_category.choices = [(cat.id, cat.title) for cat in normolized_categories]
    if request.method == "GET":
        form.title.data = category.title
        form.main_category.data = str(category.normalized_category_id)

    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.title == form.title.data, Category.id != category_id).first():
            message = {"status": 0, "text": "Категория с таким названием уже есть"}
            return render_template(
                "edit_category.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        category.title = form.title.data
        category.normalized_category_id = form.main_category.data
        if form.image.data:
            form.image.data.save(f"static/img/categories/{category_id}.jpg")
        db_sess.commit()
        return redirect("/")
    return render_template("edit_category.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/create/normalized_category", methods=["GET", "POST"])
def create_normalize_category():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    title = "Создание главной категории"
    form = NormalizedCategoryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(NormalizedCategory).filter(NormalizedCategory.title == form.title.data).first():
            message = {"status": 0, "text": "Категория с таким названием уже есть"}
            return render_template(
                "create_normalized_category.html",
                title=title,
                form=form,
                message=message,
            )
        category = NormalizedCategory(
            title=form.title.data,
        )
        db_sess.add(category)
        db_sess.commit()
        message = {"status": 1, "text": "Категория создана"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template(
        "create_normalized_category.html",
        title=title,
        form=form,
        message=smessage,
    )


@app.route("/edit/dish/<int:dish_id>", methods=["GET", "POST"])
def edit_dish(dish_id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        abort(404)
    form = DishForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    title = "Редактирование блюда"
    categories = db_sess.query(Category).all()
    checked = {di.category_id for di in db_sess.query(DishCategory.category_id).filter(DishCategory.dish_id == dish_id)}
    if not form.main_category.choices:
        normolized_categories = db_sess.query(NormalizedCategory).all()
        form.main_category.choices = [(cat.id, cat.title) for cat in normolized_categories]
    if request.method == "GET":
        form.title.data = dish.title
        form.description.data = dish.description
        form.price.data = dish.price
        form.mass.data = dish.mass
        form.main_category.data = str(dish.normalized_category_id)
    if form.validate_on_submit():
        if db_sess.query(Dish).filter(Dish.title == form.title.data, dish_id != Dish.id).first():
            message = {"status": 0, "text": "Такое блюдо уже есть в меню"}
            return render_template(
                "edit_dish.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
                categories=categories,
                checked=checked,
            )
        query = Translator(from_lang="russian", to_lang="english").translate(form.title.data)
        query = f"{form.mass.data}g " + query
        response = requests.get(api_url + query, headers={"X-Api-Key": "uKs0cNCsySCuE/7uGjOldQ==ve4Drp6e8VJSfX1V"})
        if response.status_code == requests.codes.ok:
            data = response.json()
        if data.get("items"):
            data = data["items"][0]
        else:
            data = {"calories": 0, "protein_g": 0, "fat_total_g": 0, "carbohydrates_total_g": 0}
        dish.title = form.title.data
        dish.price = form.price.data
        dish.description = form.description.data.strip()
        dish.normalized_category_id = form.main_category.data
        dish.mass = form.mass.data
        dish.calories = data["calories"]
        dish.fat = data["fat_total_g"]
        dish.protein = data["protein_g"]
        dish.carbo = data["carbohydrates_total_g"]
        db_sess.merge(dish)
        categories = {int(ct) for ct in request.form.getlist("categories")}
        for category in checked - categories:
            db_sess.delete(
                db_sess.query(DishCategory)
                .filter(DishCategory.dish_id == dish_id, DishCategory.category_id == category)
                .first(),
            )
        for category in categories - checked:
            db_sess.add(DishCategory(dish_id=dish_id, category_id=category))
        if form.image.data:
            img1 = form.image.data
            img1.save(f"static/img/dishes/{dish_id}.jpg")
        db_sess.commit()
        return redirect("/")
    return render_template(
        "edit_dish.html",
        title=title,
        form=form,
        message=smessage,
        order=session["order"],
        categories=categories,
        checked=checked,
    )


@app.route("/edit/user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not current_user.is_authenticated:
        abort(404)
    if not current_user.id == user_id:
        abort(404)
    db_sess = db_session.create_session()
    form = UserForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Изменение аккаунта"
    if request.method == "GET":
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data, current_user.id != User.id).first():
            message = {"status": 0, "text": "Такой пользователь уже есть"}
            form.email.data = current_user.email
            return render_template(
                "edit_user.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        if form.password.data:
            if form.password.data != form.password_again.data:
                message = {"status": 0, "text": "Пароли не совпадают"}
                return render_template(
                    "edit_user.html",
                    title=title,
                    form=form,
                    message=dumps(message),
                    order=session["order"],
                )
            current_user.set_password(form.password.data)
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        db_sess.merge(current_user)
        db_sess.commit()
        message = {"status": 1, "text": "Пользователь изменён"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template("edit_user.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/orders")
def orders():
    title = "Заказы"
    if not current_user.is_authenticated:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    if current_user.role == 2:
        orders = db_sess.query(Order).filter(Order.user_id == current_user.id).all()[::-1]
    elif current_user.role == 1:
        orders = db_sess.query(Order).filter(Order.status.in_([1, 2, 4])).all()[::-1]
    else:
        orders = db_sess.query(Order).all()[::-1]
    return render_template(
        "order_list.html",
        title=title,
        message=smessage,
        order=session["order"],
        orders=orders,
        STATUS=STATUS,
    )


@app.route("/create/lunch", methods=["GET", "POST"])
def create_lunch():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    form = LunchForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Создание бизнес-ланча"
    db_sess = db_session.create_session()
    categories = db_sess.query(NormalizedCategory).join(Category).join(DishCategory).all()
    voted_dishes = {}
    normalized_categories = db_sess.query(NormalizedCategory).all()
    for category in normalized_categories:
        cat_dishes = category.dishes
        voted_dishes[category.id] = {}
        for dish in cat_dishes:
            a = len(db_sess.query(Vote).filter(Vote.dish_id == dish.id).all())
            if a != 0:
                voted_dishes[category.id][dish.id] = a
        voted_dishes[category.id] = sorted(voted_dishes[category.id].items(), key=lambda item: item[1], reverse=True)
        if len(voted_dishes[category.id]) >= 3:
            voted_dishes[category.id] = [i[0] for i in voted_dishes[category.id][:3]]
        elif len(voted_dishes[category.id]) == 2:
            voted_dishes[category.id] = [i[0] for i in voted_dishes[category.id][:2]]
        elif len(voted_dishes[category.id]) == 1:
            voted_dishes[category.id] = [voted_dishes[category.id][0][0]]
        else:
            voted_dishes[category.id] = []

    if form.validate_on_submit():
        if db_sess.query(Lunch).filter(Lunch.date == form.date.data).first():
            message = {"status": 0, "text": "Бизнес-ланч на этот день уже существует"}
            return render_template(
                "create_lunch.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
                dishes=dishes,
                categories=categories,
                voted_dishes=voted_dishes,
            )
        chosen_dishes = request.form.getlist("dishes")
        if not chosen_dishes:
            message = {"status": 0, "text": "Добавьте блюда"}
            return render_template(
                "create_lunch.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
                dishes=dishes,
                categories=categories,
                voted_dishes=voted_dishes,
            )

        lunch = Lunch(price=form.price.data, date=form.date.data)
        db_sess.add(lunch)

        for dish in chosen_dishes:
            d_lunch = DishLunch(dish_id=dish)
            d_lunch.lunch = lunch
            dish = db_sess.query(Dish).get(dish)
            d_lunch.category_id = dish.normalized_category_id
            db_sess.add(d_lunch)
        db_sess.commit()
        message = {"status": 1, "text": "Бизнес-ланч создан"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template(
        "create_lunch.html",
        title=title,
        form=form,
        message=smessage,
        order=session["order"],
        categories=categories,
        voted_dishes=voted_dishes,
    )


@app.route("/lunch_list")
def lunch_list():
    title = "Бизнес-ланча"
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    db_sess = db_session.create_session()
    lunches = db_sess.query(Lunch).order_by(Lunch.date).all()[::-1]

    return render_template(
        "lunch_list.html",
        title=title,
        message=smessage,
        lunches=lunches,
    )


@app.route("/confirm/lunch/<int:lunch_id>", methods=["GET", "POST"])
def confirm_lanch(lunch_id):
    title = "Базнес-ланч"
    if current_user.is_authenticated:
        if current_user.role in [0, 1]:
            return redirect("/")
    db_sess = db_session.create_session()
    lunch = db_sess.query(Lunch).get(lunch_id)
    if not lunch:
        return redirect("/")
    if not session.get("order"):
        session["order"] = {"sum": 0}
    elif session["order"].get("lunch"):
        message = {"status": 2, "text": "В можете заказать только один бизнес-ланч"}
        session["message"] = dumps(message)
        return redirect("/")
    categories = sorted(
        {di.category for di in db_sess.query(DishLunch).filter(DishLunch.lunch_id == lunch_id)},
        key=lambda ca: ca.title,
    )
    if request.method == "POST":
        dishes = []
        for category in categories:
            if not category.lunch_dishes:
                continue
            dish = request.form.get(f"dish{category.id}")
            dishes.append(db_sess.query(DishLunch).get(dish))
        order_dishes = [
            {"id": di_l.id, "title": di_l.dish.title, "image": di_l.dish.image, "category": di_l.category.title}
            for di_l in dishes
        ]
        session["order"]["sum"] += lunch.price
        session["order"]["lunch"] = {
            "id": lunch.id,
            "price": lunch.price,
            "count": 1,
            "dishes": order_dishes,
            "date": lunch.date.strftime("%d.%m.%Y"),
        }
        message = {"status": 1, "text": "Ланч добавлен в корзину"}
        session["message"] = message
        return redirect("/")
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    return render_template(
        "confirm_lunch.html",
        title=title,
        message=smessage,
        lunch=lunch,
        categories=categories,
    )


@app.route("/profile/dish/<int:dish_id>", methods=["GET", "POST"])
def profile_dish(dish_id):
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).filter(Dish.id == dish_id).first()
    form = CommentForm()
    comments = db_sess.query(Comment).all()
    if not dish:
        abort(404)
    dish_comments = db_sess.query(Comment).filter(Comment.dish_id == dish_id).all()
    com_valuations = {}
    criteria_valuations = {}
    can_vote = False
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    if current_user.is_authenticated:
        if (
            current_user.role == 2
            and not db_sess.query(Vote).filter(Vote.user_id == current_user.id, Vote.dish_id == dish_id).all()
        ):
            can_vote = True
    for comment in dish_comments:
        com_valuations[comment.id] = db_sess.query(Valuation).filter(Valuation.comment_id == comment.id).all()
        values = com_valuations[comment.id]
        if len(values) > 0:
            for value in values:
                if not criteria_valuations.get(value.criteria.title):
                    criteria_valuations[value.criteria.title] = []
                criteria_valuations[value.criteria.title].append(value.value)
    for i in criteria_valuations:
        criteria_valuations[i] = float(str(sum(criteria_valuations[i]) / len(criteria_valuations[i]))[:3])
    criterias = db_sess.query(Criteria).all()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            message = {"status": 2, "text": "Для оставления отзыва авторизуйтесь"}
            session["message"] = dumps(message)
            return redirect(f"/profile/dish/{dish_id}")
        last_id = 1 if not comments else comments[-1].id + 1
        comment = Comment(id=last_id, comment=form.comment.data, user_id=current_user.id, dish_id=dish_id)
        db_sess.add(comment)
        for criteria in criterias:
            valuation = Valuation(
                criteria_id=criteria.id,
                comment_id=last_id,
                value=int(request.form[criteria.title]),
            )
            db_sess.add(valuation)
        db_sess.commit()
        return redirect(f"/profile/dish/{dish_id}")
    return render_template(
        "dish_profile.html",
        title=dish.title,
        message=smessage,
        dish=dish,
        criterias=criterias,
        form=form,
        dish_comments=dish_comments,
        com_valuations=com_valuations,
        criteria_valuations=criteria_valuations,
        can_vote=can_vote,
        n_date=datetime.date.today(),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    title = "Вход"
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            message = {"status": 1, "text": "Успешная авторизиция"}
            session["message"] = dumps(message)
            return redirect("/")
        message = {"status": 0, "text": "Неверный логин или пароль"}
        return render_template("login.html", title=title, form=form, message=dumps(message), order=session["order"])
    return render_template("login.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/create/post", methods=["GET", "POST"])
def create_post():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    form = PostForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Создание новости"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = Post(title=form.title.data, text=form.text.data)

        posts = db_sess.query(Post).all()
        last_id = 1 if not posts else posts[-1].id + 1
        if form.image.data:
            img1 = form.image.data
            img1.save(f"static/img/posts/{last_id}.jpg")
            post.image = f"img/posts/{last_id}.jpg"
        else:
            post.image = None
        db_sess.add(post)
        db_sess.commit()
        return redirect("/")
    return render_template("create_post.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/news")
def news():
    title = "Новости"
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).order_by(Post.date).all()[::-1]
    return render_template("news.html", title=title, message=smessage, order=session["order"], posts=posts)


@app.route("/create/criteria", methods=["GET", "POST"])
def create_criteria():
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 0:
        abort(404)
    form = CriteriaForm()
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    title = "Создание критерия"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Criteria).filter(Criteria.title == form.title.data).first():
            message = {"status": 0, "text": "Критерий с таким названием уже есть"}
            return render_template(
                "create_criteria.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
            )
        criteria = Criteria(title=form.title.data)
        db_sess.add(criteria)
        db_sess.commit()
        return redirect("/")
    return render_template("create_criteria.html", title=title, form=form, message=smessage, order=session["order"])


@app.route("/stats/<int:dish_id>/<string:date>", methods=["GET", "POST"])
def stats(dish_id, date):
    title = "Статистика"
    smessage = session["message"]
    form = StatForm(dish=dish_id, coerce=int)
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    dishes = db_sess.query(Dish).all()
    for dish in dishes:
        form.dish.choices.append((dish.id, dish.title))
    date = date.split("-")
    date = datetime.date(year=int(date[0]), month=int(date[1]), day=int(date[2]))
    stats = {}
    dish_orders = db_sess.query(DishOrder).filter(DishOrder.dish_id != None).all()
    data_dish_id = []
    data_date = []
    data_price = []
    for stat in dish_orders:
        for i in range(stat.count):
            if stat.order.edit_date <= date:
                data_dish_id.append(stat.dish_id)
                data_date.append(str(stat.order.edit_date))
                data_price.append(stat.price)
    data = pd.DataFrame({'dish_id': data_dish_id, 'дата': data_date, 'цена': data_price})
    data = data.astype({'дата': 'object'})
    stat_date = str(date)
    str_date = str(date)
    data = data.query("dish_id == @dish_id")
    print(data)
    stats["now"] = len(data.query("дата == @stat_date"))
    stat_date = str(date - datetime.timedelta(days=1))
    stats["yesterday"] = len(data.query("дата == @stat_date"))
    stat_date = str(date - datetime.timedelta(days=7))
    stats["week_ago"] = len(data.query("дата == @stat_date"))
    print(data)
    print(data.dtypes)
    stats["week"] = len(data.query("дата >= @stat_date & дата <= @str_date"))
    stat_date = str(date - datetime.timedelta(days=30))
    stats["month_ago"] = len(data.query("дата == @stat_date"))
    stats["month"] = len(data.query("дата >= @stat_date & дата <= @str_date"))
    stat_date = str(date - datetime.timedelta(days=365))
    stats["year_ago"] = len(data.query("дата == @stat_date"))
    stats["year"] = len(data.query("дата >= @stat_date & дата <= @str_date"))

    if not stats.get("now"):
        stats["now"] = 0
    if not stats.get("yesterday"):
        stats["yesterday_pred"] = stats["now"]
    else:
        stats["yesterday_pred"] = stats["yesterday"]
    if not stats.get("week_ago"):
        stats["week_ago"] = stats["yesterday"]
    if not stats.get("month_ago"):
        stats["month_ago"] = stats["week_ago"]
    if not stats.get("year_ago"):
        stats["year_ago"] = stats["month_ago"]

    predict = stats["yesterday_pred"] * 0.3 + stats["week_ago"] * 0.3 + stats["month_ago"] * 0.2 + stats["year_ago"] * 0.2
    predict = int(str(predict).split(".")[0])

    if request.method == "GET":
        form.dish.default = dish_id
        form.date.data = date
        form.data.setdefault(date)
    if form.validate_on_submit():
        dish = form.dish.data
        return redirect(f"/stats/{dish}/{form.date.data}")
    return render_template(
        "stats.html",
        title=title,
        form=form,
        message=smessage,
        order=session["order"],
        stats=stats,
        predict=predict,
    )


@app.route("/vote/<int:dish_id>")
def vote(dish_id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 2:
        abort(404)
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        abort(404)
    votes = db_sess.query(Vote).filter(Vote.user_id == current_user.id).all()
    dishes = [vote.dish_id for vote in votes]
    if dish.id in dishes:
        abort(404)
    db_sess.add(Vote(dish_id=dish.id, user_id=current_user.id))
    db_sess.commit()
    return redirect(f"/profile/dish/{dish_id}")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session["order"] = {}
    return redirect("/")


@app.route("/chats")
def chats():
    title = "Чаты"
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role == 2:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.role == 2).all()
    return render_template(
        "chats.html",
        title=title,
        message=smessage,
        order=session["order"],
        messages=smessage,
        users=users,
    )


""


@app.route("/chat/<int:user_id>")
def chat(user_id):
    title = "Чат"

    if not current_user.is_authenticated:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)
    admin, juser = sorted([user, current_user], key=lambda u: u.role)
    if admin.role not in [0, 1]:
        abort(404)
    if juser.role != 2:
        abort(404)
    if current_user.role in [0, 1]:
        messages = db_sess.query(Message).filter(
            or_(
                Message.to == user.id,
                Message.user_id == user.id,
            ),
        )
    else:
        messages = db_sess.query(Message).filter(
            or_(
                Message.to == current_user.id,
                Message.user_id == current_user.id,
            ),
        )
    return render_template(
        "chat.html",
        title=title,
        message=smessage,
        order=session["order"],
        messages=messages,
        to_user_id=user_id,
        juser=juser,
    )


@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)


@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)


@socketio.on("message")
def handle_message(data):
    room = data["room"]
    message = data["message"]
    send(message, room=room)
    db_sess = db_session.create_session()
    db_sess.add(
        Message(
            user_id=message["from"],
            to=message["to"],
            text=message["text"],
        ),
    )
    db_sess.commit()



if __name__ == "__main__":
    db_session.global_init("db/prod.db")
    fill_db(db_session.create_session())
    socketio.run(app, port=8080, host="127.0.0.1", debug=True, allow_unsafe_werkzeug=True)
