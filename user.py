from sqlalchemy.orm import Session
from data.users import User


class UserLogin:
    def from_db_by_name(self, user_name, db: Session):
        self.user = db.query(User).filter(User.name == user_name).first()
        return self

    def from_db_by_id(self, user_id, db: Session):
        self.user = db.query(User).filter(User.id == user_id).first()
        return self

    def create(self, user):
        self.user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user.id)
