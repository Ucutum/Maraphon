import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Task(SqlAlchemyBase):
    __tablename__ = "tasks"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    main_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("maraphones.id"))
    main = orm.relationship("Maraphone", back_populates="tasks")

    index = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.Date)

    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.datetime.now)

    description = sqlalchemy.Column(sqlalchemy.String)

    states = orm.relationship("State")
