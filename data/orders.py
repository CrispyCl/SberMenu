import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    is_delivery = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=0)
    delivery_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    delivery_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    edit_date = sqlalchemy.Column(sqlalchemy.DATE, nullable=False, default=datetime.date.today())

    user = orm.relationship("User", back_populates="orders")

    dishes = orm.relationship("DishOrder", back_populates="order", lazy="dynamic", cascade="all, delete-orphan")
