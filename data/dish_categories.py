import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class DishCategory(SqlAlchemyBase):
    __tablename__ = "dish_categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))

    dish = orm.relationship("Dish", back_populates="categories")
    category = orm.relationship("Category", back_populates="dishes")
