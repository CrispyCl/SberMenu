import datetime

import sqlalchemy
from data.db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = "posts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DATETIME, nullable=False, default=datetime.datetime.now())
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
