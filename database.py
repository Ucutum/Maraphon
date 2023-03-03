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
WHERE name = ?''', (name, )).fetchone()
            if not res:
                error("User not found")
                return None
            return res[0]
        except sqlite3.Error as e:
            error(e)
        return None

    def get_user_name(self, id):
        try:
            res = self.cur.execute('''SELECT name FROM users
WHERE id = ?''', (id, )).fetchone()
            if not res:
                error("User not found")
                return None
            return res[0]
        except sqlite3.Error as e:
            error(e)
        return None

    def get_user_password(self, id):
        try:
            res = self.cur.execute('''SELECT password FROM users
WHERE id = ?''', (id, )).fetchone()
            if not res:
                error("User not found")
                return None
            return res[0]
        except sqlite3.Error as e:
            error(e)
        return None

    def get_maraphon(self, id):
        try:
            res = self.cur.execute('''SELECT * FROM maraphons
WHERE id = ?''', (id, )).fetchone()
            if not res:
                error("Maraphon not found")
                return None
            maraphon = {
                "id": res[0],
                "creator": res[1],
                "title": res[2]
            }
            return maraphon
        except sqlite3.Error as e:
            error(e)
        return None

    def get_tasks(self, id):
        try:
            res = self.cur.execute('''SELECT * FROM tasks
WHERE main = ?
ORDER BY [index]''', (id, )).fetchall()
            if not res:
                error("Tasks not found")
                res = []
            tasks = []
            for e in res:
                tasks.append(
                    {
                        "id": e[0],
                        "main": e[1],
                        "index": e[2],
                        "name": e[3],
                        "date": e[4],
                        "description": e[5]
                    }
                )
            return tasks
        except sqlite3.Error as e:
            error(e)
        return None

    def get_state(self, task, user):
        try:
            res = self.cur.execute('''SELECT done FROM states
WHERE task = ? AND user = ?''', (task, user)).fetchone()
            if not res:
                error("State not found")
                return False
            return bool(res[0])
        except sqlite3.Error as e:
            error(e)
        return None
