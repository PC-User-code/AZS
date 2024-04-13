import datetime
import sqlalchemy
from sqlalchemy import orm
from . import users
from .db_session import SqlAlchemyBase


class Data(SqlAlchemyBase):
    __tablename__ = 'all_data'
    id_tranzaction = sqlalchemy.Column(sqlalchemy.Integer,
                                       primary_key=True, autoincrement=True)
    id_column = sqlalchemy.Column(sqlalchemy.Integer, index=True, nullable=False)
    dt = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False)
    volume_req = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    volume_res = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    tranz = orm.relationship('User')

    def __repr__(self):
        return f"{self.title}, {self.content}\n{self.user}"
