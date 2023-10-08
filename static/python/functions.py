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
