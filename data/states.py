import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from logging import debug


class State(SqlAlchemyBase):
    __tablename__ = "states"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True, autoincrement=True)

    task_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("tasks.id"))
    task = orm.relationship("Task", back_populates="states")

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User", back_populates="states")

    done = sqlalchemy.Column(sqlalchemy.Boolean)
