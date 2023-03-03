import logging
from logging import debug
from logging import info
from logging import warning
from logging import error

# logging.basicConfig(level=logging.INFO, filename="applog.log", filemode="w")
logging.getLogger().setLevel(logging.DEBUG)
info("Started main.py")

from flask import Flask, render_template, request, g, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from user import UserLogin
from sqlalchemy.orm import Session


info("Create app")
app = Flask(__name__)
with open("config.json") as file:
    d = json.loads(file.read())
    info("config.json" + str(d))
    app.config.from_mapping(d)

app.config.update(dict(DATABASE=os.path.join(app.root_path, "db", "database.db")))


from data import db_session


db_session.global_init(app.config["DATABASE"])


from data.maraphones import Maraphone
from data.states import State
from data.tasks import Task
from data.users import User


db: Session = db_session.create_session()
user: User = None
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
    global user
    if hasattr(current_user, "user"):
        user = current_user.__getattr__("user")
    else:
        user = None
    make_header_data()


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db_by_id(user_id, db)


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
    data = [("name", user.name), ("id", user.id)]
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
        debug(name, telegramm, password, repassword)
        new_user = User(
            name=name,
            telegramm=telegramm
            )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        redirect(url_for("login"))
    return render_template("singin.html", header=header)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        logging_user = db.query(User).filter(User.name == name).first()
        if logging_user is None:
            debug("name is unreal")
            return redirect(url_for('login'))
        password = request.form.get("password")
        if logging_user.check_password(password):
            debug("login")
            usersess = UserLogin().create(logging_user)
            login_user(usersess)
            return redirect(url_for('home'))
    return render_template("login.html", header=header)


@app.route("/maraphon/<id>", methods=["GET", "POST"])
@login_required
def maraphon(id):
    maraphon = db.get_maraphon(id)
    if not maraphon:
        return abort(404)
    print(maraphon)

    # tasks = db.get_tasks(id)
    # days = []
    # for task in tasks:
    #     days.append(
    #         (str(task["id"]), db.get_state(task["id"], current_user.id), strtooday() == task["date"]))
    # print(days)

    # if request.method == "POST":
    #     print(request.form.getlist("check"))
    #     for e in request.form.getlist("check"):
    #         ok_days = filter(lambda d: d[0] == e and d[2], days)
    #         for oe in ok_days:
    #             # update oe
    #             pass

    # parameters = {
    #     "id": id,
    #     "days": days,
    #     "title": maraphon["title"],
    #     "creator": maraphon["creator"]
    # }
    parameters = {}

    return render_template("maraphon.html", header=header, **parameters)


if __name__ == "__main__":
    app.run(debug=True)
