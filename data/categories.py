import sqlalchemy
from sqlalchemy import event, orm
from sqlalchemy.orm import Session

from data.db_session import SqlAlchemyBase
from data.dish_categories import DishCategory


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


@event.listens_for(Category, "after_update")
def after_commit_category(mapper, connect, target, *my_own_paramters):
    session = Session(bind=connect)
    dishes = session.query(DishCategory).filter(DishCategory.category_id == target.id).all()
    for di_c in dishes:
        dish = di_c.dish
        dish.normalized_category_id = target.normalized_category_id
    session.commit()
