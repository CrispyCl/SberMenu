import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class LunchOrder(SqlAlchemyBase):
    __tablename__ = "lunch_orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    lunch_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lunches.id"))
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)

    lunch = orm.relationship("Lunch", back_populates="orders")
    order = orm.relationship("Order", back_populates="lunch")

    dishes = orm.relationship("DishLunchOrder", back_populates="lunch", cascade="all, delete-orphan")
