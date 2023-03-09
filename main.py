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
from sqlalchemy.orm import Session
import datetime

from form.login import LoginForm
from form.singin import SinginForm
from form.task import TaskForm
from form.maraphon_settigns import MaraphonSettingsForm
from data import db_session


info("Create app")
app = Flask(__name__)
with open("config.json") as file:
    d = json.loads(file.read())
    info("config.json" + str(d))
    app.config.from_mapping(d)

db_session.global_init(os.path.join(app.root_path, "db", "database.db"))

from data.maraphones import Maraphone
from data.states import State
from data.tasks import Task
from data.users import User


db: Session = db_session.create_session()
header = {}


def make_header_data(url=None):
    header["registered"] = current_user.is_authenticated
    header["menu"] = [
        ("Главная", url_for("home"), False),
        ("FAQ", url_for("faq"), False),
        ("О Нас", url_for("about"), False),
        ]

    if current_user.is_authenticated:
        header["menu"].append(("Создать", url_for("create"), False))

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
    make_header_data()


login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.query(User).filter(User.id == user_id).first()


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    print("SEARCH|", request.form.get("search"))
    return redirect(url_for("maraphon", id=request.form.get("search", "0")))


@app.route("/")
@app.route("/home")
def home():
    make_header_data(url_for("home"))
    return render_template("home.html", header=header)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        m = Maraphone(
            title="NewMaraphon",
            creator_id=current_user.get_id()
        )
        db.add(m)
        db.commit()
        return redirect(url_for("maraphon", id=m.id))
    make_header_data(url_for("create"))
    maraphones = db.query(Maraphone).filter(Maraphone.creator_id == current_user.get_id()).all()
    names = list(map(lambda x: (x.title, url_for("maraphon", id=x.id)), maraphones))
    return render_template("create.html", header=header, maraphones=names)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    task = db.query(Task).filter(Task.id == id).first()

    if not task:
        return abort(404)

    if task.main.creator_id != current_user.id:
        return abort(404)

    form = TaskForm()

    if request.method == "POST":
        if "delete_task" in request.form:
            redirect_id = task.main_id
            db.delete(task)
            db.commit()
            return redirect(url_for("maraphon", id=redirect_id))

        if form.validate():
            task.name = form.name.data
            task.date = form.date.data
            task.description = form.description.data

            return redirect(url_for("maraphon", id=task.main_id))
        else:
            flash("Form is not validate.")
            return render_template(
                "edit.html", header=header, form=form,
                maraphone_id=task.main.id)

    form.name.data = task.name
    form.date.data = task.date
    form.description.data = task.description

    return render_template(
        "edit.html", header=header, form=form,
        maraphone_id=task.main.id)


def get_task_users(id):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        return []
    return set(map(
        lambda x: x.user.name, filter(lambda y: y.done, task.states)))


@app.route("/view/<int:id>")
@login_required
def view(id):
    task = db.query(Task).filter(Task.id == id).first()

    if not task:
        return abort(404)

    if task.main.creator_id != current_user.id:
        return abort(404)
    # only creator can view

    return render_template(
        "view.html", header=header, users=get_task_users(id))


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
@login_required
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

        if telegram[0] != "@":
            flash("Telegram should be similar to '@telegram'.")
            return render_template("singin.html", header=header, form=form)

        if db.query(User).filter(User.telegram == telegram).all():
            flash("This telegram is already taken.")
            return render_template("singin.html", header=header, form=form)

        if not name.strip():
            flash("Name must be specified.")
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
            userlogin = db.query(User).filter(User.name == name).first()
            login_user(userlogin)
            return redirect(url_for('home'))
        else:
            debug("password is wrong")
            flash("There is no such name or password.")
            return render_template("login.html", header=header, form=form)
    return render_template("login.html", header=header, form=form)


@app.route("/maraphon/<int:id>", methods=["GET", "POST"])
@login_required
def maraphon(id):
    id = int(id)

    maraphon = db.query(Maraphone).filter(Maraphone.id == id).first()

    if not maraphon:
        return abort(404)

    if "add_task" in request.form:
        if maraphon.creator_id != current_user.id:
            return abort(404)

        last_index = db.query(Task).filter(Task.main_id==id).order_by(Task.index).first()
        if not last_index:
            last_index = 0
        else:
            last_index = last_index.index

        task = Task(
            main_id=id,
            index=last_index,
            name="NewTask",
            date=datetime.datetime.today().date(),
            description="-"
            )
        db.add(task)
        db.commit()

        return redirect(url_for("edit", id=task.id))

    is_creator = str(maraphon.creator_id) == str(current_user.get_id())

    tasks = db.query(Task).filter(Task.main_id == id).order_by(Task.date).all()
    days = []
    for task in tasks:
        current_state = db.query(State).filter(State.task_id == task.id, State.user_id == current_user.get_id()).first()
        if current_state is None:
            current_state = State(task_id=task.id, user_id=current_user.get_id(), done=False)
            db.add(current_state)
            db.commit()
        if is_creator:
            done_users = get_task_users(task.id)
        else:
            done_users = []
        days.append((
            task.id,
            task.name,
            current_state.done,
            datetime.datetime.today().date() == task.date,
            task.description,
            task.date,
            done_users))

    if request.method == "POST":
        for element_id in list(map(lambda x: x[0], days)):
            ok_days = list(filter(lambda d: d[0] == element_id and d[3], days))

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
            db.commit()
        return redirect(url_for("maraphon", id=id))

    parameters = {
        "id": id,
        "title": maraphon.title,
        "creator": maraphon.creator.name,
        "days": days,
        "is_creator": is_creator,
        "maraphone_name": maraphon.title
    }

    return render_template("maraphon.html", header=header, **parameters)


@app.route("/maraphon_settigns/<int:id>", methods=["GET", "POST"])
@login_required
def maraphon_settings(id):
    maraphon = db.query(Maraphone).filter(Maraphone.id == id).first()

    if not maraphon:
        return abort(404)

    if maraphon.creator_id != current_user.id:
        return abort(404)

    form = MaraphonSettingsForm()

    if form.validate_on_submit():
        maraphon.title = form.title.data
        db.commit()
        return redirect(url_for("maraphon", id=maraphon.id))

    form.title.content = maraphon.title

    return render_template(
        "maraphon_settings.html", header=header, form=form,
        maraphone_id=maraphon.id)


if __name__ == "__main__":
    app.run(debug=True)
