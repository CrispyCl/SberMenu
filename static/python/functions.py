import datetime

from data.orders import Order
from data.users import User


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


def clear_db(db_sess):
    date = datetime.date.today() - datetime.timedelta(days=1)
    orders = db_sess.query(Order).filter(Order.status.in_([0, 3]), Order.edit_date < date).all()
    for order in orders:
        db_sess.delete(order)
    db_sess.commit()
