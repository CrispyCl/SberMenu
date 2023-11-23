import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Criteria(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "criterias"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
        }


valuations = orm.relationship("Valuation", back_populates="criteria")
