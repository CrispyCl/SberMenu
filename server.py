import datetime
from json import dumps

from flask import abort, Flask, redirect, render_template, request, session
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
from flask_socketio import SocketIO
from PIL import Image
from static.python.functions import clear_db, create_main_admin

from data import db_session
from data.categories import Category
from data.comments import Comment
from data.criterias import Criteria
from data.dish_categories import DishCategory
from data.dish_orders import DishOrder
from data.dishes import Dish
from data.dishes_lunch import DishLunch
from data.lunches import Lunch
from data.orders import Order
from data.users import User
from data.valuations import Valuation
from forms.category import CategoryForm
from forms.comment import CommentForm
from forms.dish import DishForm
from forms.login import LoginForm
from forms.lunch import LunchForm
from forms.user import UserForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secret_key"
socketio = SocketIO(app)

ST_message = {"status": 404, "text": ""}
STATUS = {1: "В процессе", 2: "Приготовлен", 3: "Выдан", 0: "Отменён"}
current_user.is_authenticated: bool

login_manager = LoginManager()
login_manager.init_app(app)


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

    return render_template("index.html", message=smessage, order=session["order"], categories=categories)


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
    session["order"]["sum"] = sum(map(lambda v: dc[v]["count"] * dc[v]["price"] if v != "sum" else 0, dc))
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
    if order.status in [0, 3]:
        abort(404)
    if current_user.role == 2 and current_user.id != order.user.id:
        abort(404)
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
            if k == "sum":
                continue
            if int(counts[i]) == 0:
                to_del.add(k)
                continue
            session["order"][k]["count"] = int(counts[i])
        for k in to_del:
            del session["order"][k]
        dc = session["order"]
        session["order"]["sum"] = sum(map(lambda v: dc[v]["count"] * dc[v]["price"] if v != "sum" else 0, dc))

        if not current_user.is_authenticated:
            message = {"status": 2, "text": "Для оформления заказа авторизуйтесь"}
            session["message"] = dumps(message)
            return redirect("/login")
        if list(session["order"]) == ["sum"]:
            message = {"status": 1, "text": "Заказ отменён"}
            session["message"] = dumps(message)
            session["order"] = {}
            return redirect("/")
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).all()
        last_id = 1 if not orders else orders[-1].id + 1
        order = Order(
            id=last_id,
            user_id=current_user.id,
            status=1,
            price=session["order"]["sum"],
        )
        db_sess.add(order)
        for k in session["order"]:
            if k == "sum":
                continue
            el = session["order"][k]

            dish_order = DishOrder(
                dish_id=int(k),
                order_id=last_id,
                count=el["count"],
                price=el["price"],
            )
            db_sess.add(dish_order)
        db_sess.commit()
        message = {"status": 1, "text": "Заказ создан"}
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
        dish = Dish(title=form.title.data, price=form.price.data, description=form.description.data.strip())

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
        "create_dish.html", title=title, form=form, message=smessage, order=session["order"], categories=categories
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
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Category).filter(Category.title == form.title.data).first():
            message = {"status": 0, "text": "Категория с таким названием уже есть"}
            return render_template(
                "create_category.html", title=title, form=form, message=dumps(message), order=session["order"]
            )
        category = Category(title=form.title.data)

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
        return redirect("/")
    return render_template("create_category.html", title=title, form=form, message=smessage, order=session["order"])


# @app.route("/chat/<int:user_id>")
# def chat(user_id):
#     if not current_user.is_authenticated:
#         abort(404)
#     if user_id == 0 and current_user.role != 2:
#         abort(404)
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.id == user_id).first()
#     if not user:
#         abort(404)
#     if user.role == current_user.role:
#         abort(404)
#     messages = db_sess.query(Message)


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
                "register_user.html", title=title, form=form, message=dumps(message), order=session["order"]
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            message = {"status": 0, "text": "Такой пользователь уже есть"}
            return render_template(
                "register_user.html", title=title, form=form, message=dumps(message), order=session["order"]
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
        message = {"status": 1, "text": "Успешная авторизиция"}
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
                "register_spec.html", title=title, form=form, message=dumps(message), order=session["order"]
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            message = {"status": 0, "text": "Такой пользователь уже есть"}
            return render_template(
                "register_spec.html", title=title, form=form, message=dumps(message), order=session["order"]
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
    if request.method == "GET":
        form.title.data = category.title
    if form.validate_on_submit():
        if db_sess.query(Category).filter(Category.title == form.title.data, Category.id != category_id).first():
            message = {"status": 0, "text": "Категория с таким названием уже есть"}
            return render_template(
                "edit_category.html", title=title, form=form, message=dumps(message), order=session["order"]
            )
        category.title = form.title.data
        if form.image.data:
            form.image.data.save(f"static/img/categories/{category_id}.jpg")
        db_sess.commit()
        return redirect("/")
    return render_template("edit_category.html", title=title, form=form, message=smessage, order=session["order"])


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
    checked = list(
        map(lambda v: v.category_id, db_sess.query(DishCategory).filter(DishCategory.dish_id == dish_id).all())
    )
    if request.method == "GET":
        form.title.data = dish.title
        form.description.data = dish.description
        form.price.data = dish.price
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
        dish.title = form.title.data
        dish.price = form.price.data
        dish.description = form.description.data.strip()
        db_sess.merge(dish)
        categories = request.form.getlist("categories")
        for category in checked:
            db_sess.delete(
                db_sess.query(DishCategory)
                .filter(DishCategory.dish_id == dish_id, DishCategory.category_id == category)
                .first()
            )
        for category in categories:
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
                "edit_user.html", title=title, form=form, message=dumps(message), order=session["order"]
            )
        if form.password.data:
            if form.password.data != form.password_again.data:
                message = {"status": 0, "text": "Пароли не совпадают"}
                return render_template(
                    "edit_user.html", title=title, form=form, message=dumps(message), order=session["order"]
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
    if not current_user.is_authenticated:
        abort(404)
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    if current_user.role == 2:
        orders = db_sess.query(Order).filter(Order.user_id == current_user.id).join(DishOrder).all()[::-1]
    elif current_user.role == 1:
        orders = db_sess.query(Order).filter(Order.status.in_([1, 2])).join(DishOrder).all()[::-1]
    else:
        orders = db_sess.query(Order).join(DishOrder).all()[::-1]

    return render_template(
        "order_list.html",
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

    title = "Создание бизнесс-ланча"
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).join(DishCategory).all()

    if form.validate_on_submit():
        if db_sess.query(Lunch).filter(Lunch.date == form.date.data).first():
            message = {"status": 0, "text": "Бизнесс-ланч на этот день уже существует"}
            return render_template(
                "create_lunch.html",
                title=title,
                form=form,
                message=dumps(message),
                order=session["order"],
                dishes=dishes,
                categories=categories,
            )

        lunch = Lunch(price=form.price.data, date=form.date.data)
        db_sess.add(lunch)

        chosen_dishes = request.form.getlist("dishes")
        for dish in chosen_dishes:
            d_lunch = DishLunch(dish_id=dish)
            d_lunch.lunch = lunch
            db_sess.add(d_lunch)
        db_sess.commit()
        message = {"status": 1, "text": "Бизнесс-ланч создан"}
        session["message"] = dumps(message)
        return redirect("/")
    return render_template(
        "create_lunch.html",
        title=title,
        form=form,
        message=smessage,
        order=session["order"],
        categories=categories,
    )


@app.route("/profile/dish/<int:dish_id>", methods=["GET", "POST"])
def profile_dish(dish_id):
    db_sess = db_session.create_session()
    dish = db_sess.query(Dish).filter(Dish.id == dish_id).first()
    form = CommentForm()
    comments = db_sess.query(Comment).all()
    last_id = 1 if not comments else comments[-1].id + 1
    if not dish:
        abort(404)
    dish_comments = db_sess.query(Comment).filter(Comment.dish_id == dish_id).all()
    valuations = {}
    for comment in dish_comments:
        valuations[comment.id] = list(
            map(lambda di: di, db_sess.query(Valuation).filter(Valuation.comment_id == comment.id).all())
        )
    print(valuations)
    criterias = db_sess.query(Criteria).all()
    criteria_count = len(criterias)
    if form.validate_on_submit():
        print(1)
        comment = Comment(comment=form.comment.data, user_id=current_user.id, dish_id=dish_id)
        for i in range(criteria_count):
            valuation = Valuation(
                criteria_id=criterias[i].id,
                comment_id=last_id,
                value=int(request.form[criterias[i].title]),
            )
            db_sess.add(valuation)
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f"/profile/dish/{dish_id}")
    return render_template(
        "dish_profile.html",
        title=dish.title,
        message=ST_message,
        dish=dish,
        criterias=criterias,
        form=form,
        dish_comments=dish_comments,
        valuations=valuations,
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


if __name__ == "__main__":
    db_session.global_init("db/GriBD.db")
    create_main_admin(db_session.create_session())
    clear_db(db_session.create_session())
    socketio.run(app, port=8080, host="127.0.0.1", debug=True)
