import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    telegram = sqlalchemy.Column(
        sqlalchemy.String,
        unique=True,
        nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(
        sqlalchemy.Date,
        default=datetime.datetime.now)
    maraphones = orm.relationship("Maraphone", back_populates="creator")

    states = orm.relationship("State")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user.id)
