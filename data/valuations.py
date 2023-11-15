import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Valuation(SqlAlchemyBase):
    __tablename__ = "valuations"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    criteria_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("criterias.id"))
    comment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("comments.id"))
    value = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    criteria = orm.relationship("Criteria")
