from data.normalized_categories import NormalizedCategory
from data.users import User


def fill_db(db_sess):
    create_main_admin(db_sess)
    create_base_category(db_sess)


def create_main_admin(db_sess):
    res = db_sess.query(User).all()
    if res:
        return
    user = User(
        id=1,
        email="main_admin@mail.ru",
        role=0,
    )
    user.set_password("111")
    db_sess.add(user)
    db_sess.commit()

    user = User(
        id=2,
        email="spec@mail.ru",
        role=1,
    )
    user.set_password("111")
    db_sess.add(user)
    db_sess.commit()


def create_base_category(db_sess):
    res = db_sess.query(NormalizedCategory).all()
    if res:
        return
    category = NormalizedCategory(
        id=1,
        title="Другое",
    )
    db_sess.add(category)
    db_sess.commit()
