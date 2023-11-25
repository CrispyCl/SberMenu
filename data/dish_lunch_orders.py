import sqlalchemy
from sqlalchemy import orm


from data.db_session import SqlAlchemyBase


class DishLunchOrder(SqlAlchemyBase):
    __tablename__ = "dish_lunch_orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dish_lunches.id"))
    lunch_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lunch_orders.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="Другое")

    dish = orm.relationship("DishLunch", back_populates="orders")
    lunch = orm.relationship("LunchOrder", back_populates="dishes")
