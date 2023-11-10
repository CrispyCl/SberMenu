import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "user_id": self.user_id
        }

    user = orm.relationship("User")
    dish = orm.relationship("Dish")
