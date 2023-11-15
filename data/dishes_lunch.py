import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class DishLunch(SqlAlchemyBase):
    __tablename__ = "dish_lunches"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))
    lunch_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    dish = orm.relationship("Dish")
