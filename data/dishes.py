import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Dish(SqlAlchemyBase):
    __tablename__ = "dishes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mass = sqlalchemy.Column(sqlalchemy.Integer, default=100)
    calories = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    fat = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    protein = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    carbo = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    normalized_category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("normalized_categories.id"),
        default=1,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "image": self.image,
        }

    orders = orm.relationship("DishOrder", back_populates="dish", lazy="dynamic")
    categories = orm.relationship("DishCategory", back_populates="dish", lazy="dynamic", cascade="all, delete-orphan")

    normalized_category = orm.relationship("NormalizedCategory", back_populates="dishes")
    votes = orm.relationship("Vote", back_populates="dish", lazy="dynamic", cascade="all, delete-orphan")
