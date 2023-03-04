import logging
from logging import debug
from logging import info
from logging import warning

# logging.basicConfig(level=logging.INFO, filename="applog.log", filemode="w")
logging.getLogger().setLevel(logging.DEBUG)
info("Started main.py")

from flask import Flask, render_template, request, abort, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from userlogin import UserLogin
from sqlalchemy.orm import Session
import datetime

from form.login import LoginForm
from form.singin import SinginForm


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
        ("Главная", url_for("home"), False),
        ("FAQ", url_for("faq"), False),
        ("О Нас", url_for("about"), False)
        ]
    if url == url_for("account"):
        header["account"] = True
    else:
        header["account"] = False

    if url is not None:
        for i in range(len(header["menu"])):
            if header["menu"][i][1] == url:
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
    form = SinginForm()
    if form.validate_on_submit():
        telegram = form.telegram.data
        name = form.name.data
        password = form.password.data
        password_again = form.password_again.data

        if len(telegram) <= 1:
            flash("Telegram must be specified.")
            return render_template("singin.html", header=header, form=form)
        if telegram[0] != "@":
            flash("Telegram should be similar to '@telegram'.")
            return render_template("singin.html", header=header, form=form)

        if db.query(User).filter(User.telegram == telegram).all():
            flash("This telegram is already taken.")
            return render_template("singin.html", header=header, form=form)

        if not name.strip():
            flash("Name must be specified.")
            return render_template("singin.html", header=header, form=form)

        if len(name) <= 5:
            flash("The name should be longer 5 characters. (>= 6)")
            return render_template("singin.html", header=header, form=form)

        if db.query(User).filter(User.name == name).all():
            flash("This name is already taken.")
            return render_template("singin.html", header=header, form=form)

        if password != password_again:
            flash("The password was repeated incorrectly.")
            return render_template("singin.html", header=header, form=form)

        debug(f"singin {telegram} {name}")
        new_user = User(
            name=name,
            telegram=telegram
            )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        return redirect(url_for("login"))
    return render_template("singin.html", header=header, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        logging_user = db.query(User).filter(User.name == name).first()
        if logging_user is None:
            debug("name is unreal")
            flash("There is no such name or password.")
            return render_template("login.html", header=header, form=form)
        password = form.password.data
        if logging_user.check_password(password):
            debug(f"login {name}")
            usersess = UserLogin().create(logging_user)
            login_user(usersess)
            return redirect(url_for('home'))
        else:
            debug("password is wrong")
            flash("There is no such name or password.")
            return render_template("login.html", header=header, form=form)
    return render_template("login.html", header=header, form=form)


@app.route("/maraphon/<id>", methods=["GET", "POST"])
@login_required
def maraphon(id):
    maraphon = db.query(Maraphone).filter(Maraphone.id == id).first()
    print(maraphon)

    if not maraphon:
        return abort(404)

    tasks = db.query(Task).filter(Task.main_id == id).all()
    days = []
    for task in tasks:
        current_state = db.query(State).filter(State.task_id == task.id, State.user_id == current_user.get_id()).first()
        if current_state is None:
            current_state = State(task_id=task.id, user_id=current_user.get_id(), done=False)
            db.add(current_state)
            db.commit()
        days.append((
            task.id,
            task.name,
            current_state.done,
            datetime.datetime.today().date() == task.date,
            task.description))
    print(days)

    # day
    # (id, name, done, can_change)

    if request.method == "POST":
        checked = request.form.getlist("check")
        for element_id in list(map(lambda x: x[0], days)):
            ok_days = list(filter(lambda d: d[0] == element_id and d[3], days))
            # days with id == element_id
            print(ok_days)
            if len(ok_days) == 0:
                continue
            if len(ok_days) > 1:
                warning("len(days) > 1")
            ok_day = ok_days[0]
            current_state = db.query(State).filter(State.task_id == ok_day[0], State.user_id == current_user.get_id()).first()
            # current State
            if not current_state:
                warning("not current state")
                abort(400)
            current_state.done = str(element_id) in request.form.getlist("check")
            print(current_state.done)
            db.commit()
        return redirect(url_for("maraphon", id=id))

    parameters = {
        "id": id,
        "title": maraphon.title,
        "creator": maraphon.creator.name,
        "days": days
    }

    return render_template("maraphon.html", header=header, **parameters)


if __name__ == "__main__":
    app.run(debug=True)
