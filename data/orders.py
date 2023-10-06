import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    user = orm.relationship("User")
