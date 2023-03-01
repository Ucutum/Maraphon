class User:
    def from_db_by_name(self, user_name, db):
        self.id = db.get_user_id(user_name)
        self.name = user_name
        return self

    def from_db_by_id(self, user_id, db):
        self.name = db.get_user_name(user_id)
        self.id = user_id
        return self

    def create(self, id, name):
        self.id = id
        self.name = name
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
