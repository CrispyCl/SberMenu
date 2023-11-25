import sqlalchemy

from data.db_session import SqlAlchemyBase


class Stat(SqlAlchemyBase):
    __tablename__ = "stats"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dishes.id"))
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.DATE, nullable=False)
