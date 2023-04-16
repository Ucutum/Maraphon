import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "tasks"
    serialize_only = (
        "id", "main_id", "name", "date",
        "created_date", "description", "main.creator_id")

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    main_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("maraphones.id"))
    main = orm.relationship("Maraphone", back_populates="tasks")

    name = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.Date)

    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.datetime.now)

    description = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String, default="-")

    states = orm.relationship("State")
