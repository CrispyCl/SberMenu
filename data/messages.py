import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = "messages"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    test = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user = orm.relationship("User", back_populates="messages")
