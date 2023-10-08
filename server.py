from json import dumps, loads

from PIL import Image
from data import db_session
from data.categories import Category
from data.dish_categories import DishCategory
from data.dishes import Dish
from data.users import User
from flask import Flask, abort, redirect, render_template, request, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from forms.category import CategoryForm
from forms.dish import DishForm
from forms.login import LoginForm
from forms.user import UserForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secret_key"
ST_message = {"status": 404, "text": ""}

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    if not session.get("message"):
        session["message"] = dumps(ST_message)
    if not session.get("order"):
        session["order"] = []
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    dishes = {}
    for category in categories:
        dishes[category.id] = list(
            map(lambda di: di.dish, db_sess.query(DishCategory).filter(DishCategory.category_id == category.id).all())
        )
    return render_template("index.html", message=smessage, order=session["order"], categories=categories, dishes=dishes)


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
        dish = Dish(title=form.title.data, price=form.price.data, description=form.description.data)

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
        return redirect("/")
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
        if db_sess.query(Category).filter(Category.title == form.title.data,
                                          Category.id != category_id).first():
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    smessage = session["message"]
    session["message"] = dumps(ST_message)
    title = "Вход"
    print(smessage)
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
    session["order"] = []
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("db/GriBD.db")
    app.run(port=8080, host="127.0.0.1", debug=True)
