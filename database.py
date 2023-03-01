import sqlite3
import uuid


def error(e):
    print("ERROR|", e)


class Database:
    def __init__(self, conn) -> None:
        self.conn: sqlite3.Connection = conn
        self.cur: sqlite3.Cursor = conn.cursor()

    @property
    def random_id(self):
        return uuid.uuid4()

    def add_user(self, name, password):
        try:
            if self.cur.execute('''SELECT * FROM users
WHERE name = ?''', (name, )).fetchone():
                error("Name already used")
                return False
            self.cur.execute(
                '''INSERT INTO users VALUES (?, ?, ?)''',
                (str(self.random_id), str(name), str(password)))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            error(e)
        return False

    def get_user_id(self, name):
        try:
            res = self.cur.execute('''SELECT id FROM users
WHERE name = ?''', (name, )).fetchone()[0]
            if not res:
                error("User not found")
                return None
            return res
        except sqlite3.Error as e:
            error(e)
        return None

    def get_user_name(self, id):
        try:
            res = self.cur.execute('''SELECT name FROM users
WHERE id = ?''', (id, )).fetchone()[0]
            if not res:
                error("User not found")
                return None
            return res
        except sqlite3.Error as e:
            error(e)
        return None

    def get_user_password(self, id):
        try:
            res = self.cur.execute('''SELECT password FROM users
WHERE id = ?''', (id, )).fetchone()[0]
            if not res:
                print("User not found")
                return None
            return res
        except sqlite3.Error as e:
            error(e)
        return None
