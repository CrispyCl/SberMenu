import sqlalchemy
from sqlalchemy import event, orm

from data.db_session import SqlAlchemyBase


class NormalizedCategory(SqlAlchemyBase):
    __tablename__ = "normalized_categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    lunch_dishes = orm.relationship("DishLunch", back_populates="category", lazy="dynamic", cascade="all, delete-orphan")
    categories = orm.relationship("Category", back_populates="normalized_category", cascade="all, delete-orphan")


@event.listens_for(NormalizedCategory, "before_delete")
def after_delete_normolize_category(mapper, connect, target, *my_own_paramters):
    base_category = connect.query(NormalizedCategory).get(1)
    for cat in target.categories:
        cat.category = base_category
    connect.commit()
    raise Exception("Не удаляй")
