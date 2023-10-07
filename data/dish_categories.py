import sqlalchemy

from .db_session import SqlAlchemyBase


class DishCategory(SqlAlchemyBase):
    __tablename__ = "dish_categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))
    category_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
