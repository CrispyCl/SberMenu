import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = "categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    normalized_category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("normalized_categories.id"),
    )
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    dishes = orm.relationship("DishCategory", back_populates="category", lazy="dynamic", cascade="all, delete-orphan")
    normalized_category = orm.relationship("NormalizedCategory", back_populates="categories")
