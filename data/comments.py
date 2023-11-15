import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
import datetime as dt
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))
    datetime = sqlalchemy.Column(sqlalchemy.DATETIME, default=dt.datetime.now)
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "user_id": self.user_id
        }

    dish = orm.relationship("Dish")
