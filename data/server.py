import datetime
import sqlalchemy
from sqlalchemy import orm
from . import users
from .db_session import SqlAlchemyBase


class Server(SqlAlchemyBase):
    __tablename__ = 'all_data'
    id_tranzaction = sqlalchemy.Column(sqlalchemy.Integer,
                                       primary_key=True, autoincrement=True)
    id_column = sqlalchemy.Column(sqlalchemy.Integer, index=True, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    volume_req = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    volume_res = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    tranzaction = orm.relationship("User", back_populates="user")

    def __repr__(self):
        return f"{self.id_tranzaction}, {self.id_column}, {self.date}, {self.time}, {self.user_id}, {self.volume_req}, {self.volume_res}"
