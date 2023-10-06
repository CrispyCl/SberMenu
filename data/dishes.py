import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Dish(SqlAlchemyBase):
    __tablename__ = "dishes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)


orders = orm.relationship("DishOrder", back_populates="dish")
