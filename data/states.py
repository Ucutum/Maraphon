import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class State(SqlAlchemyBase, SerializerMixin):
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
