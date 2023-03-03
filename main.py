from flask import Flask, render_template, request, g, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from database import Database
import json
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from user import User
from datetime import datetime

app = Flask(__name__)
with open("config.json") as file:
    d = json.loads(file.read())
    print(d)
    app.config.from_mapping(d)

app.config.update(dict(DATABASE=os.path.join(app.root_path, "database.db")))


def connect_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('create_tables.sql', mode='r') as file:
        db.cursor().executescript(file.read())
    db.commit()
    db.close()


def get_db() -> Database:
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return Database(g.link_db)


db: Database = None
header = {}


def make_header_data(url=None):
    header["registered"] = current_user.is_authenticated
    header["menu"] = [
        ("Главная", "home", False),
        ("FAQ", "faq", False),
        ("О Нас", "about", False)
        ]
    if url == url_for("account"):
        header["account"] = True
    else:
        header["account"] = False

    if url is not None:
        for i in range(len(header["menu"])):
            if url_for(header["menu"][i][1]) == url:
                header["menu"][i] = (
                    header["menu"][i][0], header["menu"][i][1], True)
            else:
                header["menu"][i] = (
                    header["menu"][i][0], header["menu"][i][1], False)


@app.before_request
def before_request():
    global db
    db = get_db()
    make_header_data()


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User().from_db_by_id(user_id, db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


def strtooday():
    date = datetime.today()
    day = date.day
    month = date.month
    year = date.year
    strdate = f"{str(year).rjust(4, '0')}.{str(month).rjust(2, '0')}" +\
        f".{str(day).rjust(2, '0')}"
    return strdate


@app.route("/search", methods=["GET", "POST"])
def search():
    print("SEARCH|", request.form.get("search"))
    return redirect(url_for("maraphon", id=request.form.get("search", "0")))


@app.route("/")
@app.route("/home")
def home():
    make_header_data(url_for("home"))
    return render_template("home.html", header=header)


@app.route("/faq")
def faq():
    make_header_data(url_for("faq"))
    return render_template("faq.html", header=header)


@app.route("/about")
def about():
    make_header_data(url_for("about"))
    return render_template("about.html", header=header)


@app.route("/account")
@login_required
def account():
    make_header_data(url_for("account"))
    data = [("name", current_user.name), ("id", current_user.id)]
    return render_template("account.html", header=header, data=data)


@app.route("/logout")
def logout():
    print("logout")
    logout_user()
    return redirect(url_for("home"))


@app.route("/singin", methods=["GET", "POST"])
def singin():
    if request.method == "POST":
        name = request.form.get("name")
        telegramm = request.form.get("telegramm")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        if password != repassword:
            return abort(400)
        print(name, telegramm, password, repassword)
        if not db.add_user(name, generate_password_hash(password)):
            return abort(400)
    return render_template("singin.html", header=header)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        id = db.get_user_id(name)
        if id is None:
            return redirect(url_for('login'))
        password = request.form.get("password")
        if check_password_hash(db.get_user_password(id), password):
            user = User().create(id, name)
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", header=header)


@app.route("/maraphon/<id>", methods=["GET", "POST"])
@login_required
def maraphon(id):
    maraphon = db.get_maraphon(id)
    if not maraphon:
        return abort(404)
    print(maraphon)

    tasks = db.get_tasks(id)
    days = []
    for task in tasks:
        days.append(
            (str(task["id"]), db.get_state(task["id"], current_user.id), strtooday() == task["date"]))
    print(days)

    if request.method == "POST":
        print(request.form.getlist("check"))
        for e in request.form.getlist("check"):
            ok_days = filter(lambda d: d[0] == e and d[2], days)
            for oe in ok_days:
                # update oe
                pass

    parameters = {
        "id": id,
        "days": days,
        "title": maraphon["title"],
        "creator": maraphon["creator"]
    }
    return render_template("maraphon.html", header=header, **parameters)


if __name__ == "__main__":
    app.run(debug=True)
