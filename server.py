from flask import Flask, render_template, request, abort, redirect, url_for, flash, jsonify
import os
import json
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import datetime
import uuid

from form.login import LoginForm
from form.singin import SinginForm
from form.task import TaskForm
from form.maraphon_settigns import MaraphonSettingsForm
from data import db_session

app = Flask(__name__)
with open("config.json") as file:
    d = json.loads(file.read())
    app.config.from_mapping(d)

db_session.global_init(os.path.join(app.root_path, "db", "database.db"))

from data.maraphones import Maraphone
from data.states import State
from data.tasks import Task
from data.users import User

from flask_restful import Api, Resource, reqparse

api = Api(app)

api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument("api_key", required=True, type=str)


class MaraphoneApi(Resource):
    def get(self, id):
        args = api_key_parser.parse_args()
        if not check_api_key(args.api_key):
            return jsonify({"error": 403, "message":"api key not found"})

        db = db_session.create_session()
        m = db.query(Maraphone).filter(Maraphone.id == id).first()
        if m is None:
            return jsonify({"error": 430, "message":"maraphone not found"})
        return jsonify({"maraphone": m.to_dict()})
    

class TasksListApi(Resource):
    def get(self, maraphone_id):
        args = api_key_parser.parse_args()
        if not check_api_key(args.api_key):
            return jsonify({"error": 403, "message":"api key not found"})

        db = db_session.create_session()

        m = db.query(Maraphone).filter(Maraphone.id == maraphone_id).first()
        if m is None:
            return jsonify({"error": 430, "message":"maraphone not found"})

        t = db.query(Task).filter(Task.main_id == maraphone_id).all()
        return jsonify({"tasks": [i.to_dict() for i in t]})


parser = reqparse.RequestParser()
parser.add_argument("maraphone_id", required=True, type=int)
parser.add_argument("name", required=True, type=str)
parser.add_argument("date", required=True, type=str)
parser.add_argument("description", required=True, type=str)
parser.add_argument("api_key", required=True, type=str)


def check_api_key(api_key):
    db = db_session.create_session()
    return bool(db.query(User).filter(User.api_key == api_key).first())


class TasksApi(Resource):
    def get(self, task_id):
        db = db_session.create_session()
        args = api_key_parser.parse_args()
        if not check_api_key(args.api_key):
            return jsonify({"error": 403, "message":"api key not found"})

        t = db.query(Task).filter(Task.id == task_id).first()
        if t is None:
            return jsonify({"error": 432, "message":"task not found"})
        
        return jsonify(t.to_dict())
    
    def post(self, task_id):
        args = parser.parse_args()
        db = db_session.create_session()
        if not check_api_key(args.api_key):
            return jsonify({"error": 403, "message":"api key not found"})

        m = db.query(Maraphone).filter(Maraphone.id == args.maraphone_id).first()
        if m is None:
            return jsonify({"error": 430, "message":"maraphone not found"})
        
        u = db.query(User).filter(User.api_key == args.api_key).first()
        if u is None:
            return jsonify({"error": 403, "message":"not enough rights"})
        if m.creator_id != u.id:
            return jsonify({"error": 403, "message":"not enough rights"})
        
        time_str = args.date
        time_format = "%Y.%m.%d"

        try:
            time_obj = datetime.datetime.strptime(time_str, time_format)
        except ValueError:
            return jsonify({"error": 400, "message":"error with time"})

        t = Task(
            main_id=args.maraphone_id,
            name=args.name,
            date=time_obj,
            description=args.description)
        
        db.add(t)
        db.commit()
        return jsonify({"message":"ok"})

api.add_resource(MaraphoneApi, "/api/maraphone/<int:id>")
api.add_resource(TasksListApi, "/api/task_list/<int:maraphone_id>")
api.add_resource(TasksApi, "/api/task/<int:task_id>")


header = {}


def make_header_data(url=None):
    header["registered"] = current_user.is_authenticated
    header["menu"] = [
        ("Home", url_for("home"), False),
        ("FAQ", url_for("faq"), False),
        ("About", url_for("about"), False),
        ]

    if current_user.is_authenticated:
        header["menu"].append(("My maraphons", url_for("create"), False))

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

login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).filter(User.id == user_id).first()


@app.errorhandler(404)
def error404(e):
    return render_template("404error.html")


@app.errorhandler(500)
def error500(e):
    return render_template("500error.html")


@app.errorhandler(403)
def error403(e):
    return render_template("403error.html")


@app.errorhandler(400)
def error400(e):
    return render_template("400error.html")


def searching(db, q):
    a = db.query(Maraphone).filter(Maraphone.title.contains(f"{ q }")).all()
    return list(map(lambda x: (x.title, x.id), a))


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    db = db_session.create_session()
    mid = request.form.get("search", None)
    if mid is None:
        abort(404)
    elif request.form.get("search").isdigit():
        m = db.query(Maraphone).filter(Maraphone.id == mid).first()
        if m is None:
            return render_template(
                "search_result.html", header=header,
                maraphones=searching(db, mid),
                question=mid)
        else:
            return redirect(url_for("maraphon", id=request.form.get("search", "0")))
    else:
        return render_template(
            "search_result.html", header=header,
            maraphones=searching(db, mid),
            question=mid)


@app.route("/")
@app.route("/home")
def home():
    db = db_session.create_session()
    maraphones = list(map(
        lambda x: (x.title, x.id),
        (db.query(Maraphone).order_by(Maraphone.created_date).all()[::-1])[:10]))
    make_header_data(url_for("home"))
    return render_template("home.html", header=header, maraphones=maraphones)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    db = db_session.create_session()

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


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    db = db_session.create_session()

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

            if 'image' not in request.files:
                pass
            else:
                image = request.files["image"]
                if not image.filename.strip():
                    pass
                elif allowed_file(image.filename):
                    name = str(uuid.uuid4()) + image.filename[image.filename.rfind("."):]
                    image.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
                    task.image = name
                else:
                    flash("Image is not validate.")
                    return render_template(
                        "edit.html", header=header, form=form,
                        maraphone_id=task.main.id,
                        image_path="/" + app.config["UPLOAD_FOLDER"] + "/" + task.image)
            db.commit()

            return redirect(url_for("maraphon", id=task.main_id))
        else:
            flash("Form is not validate.")
            return render_template(
                "edit.html", header=header, form=form,
                maraphone_id=task.main.id,
                image_path="/" + app.config["UPLOAD_FOLDER"] + "/" + task.image)

    form.name.data = task.name
    form.date.data = task.date
    form.description.data = task.description

    if task.image is None:
        image_path = "None"
    else:
        image_path = task.image

    return render_template(
        "edit.html", header=header, form=form,
        maraphone_id=task.main.id,
        image_path="/" + app.config["UPLOAD_FOLDER"] + "/" + task.image)


def get_task_users(id):
    db = db_session.create_session()

    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        return []
    return set(map(
        lambda x: x.user.name, filter(lambda y: y.done, task.states)))


@app.route("/view/<int:id>")
@login_required
def view(id):
    db = db_session.create_session()

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
    data = [
        ("name", current_user.name), ("id", current_user.id),
        (
        "api_key",
         current_user.api_key if current_user.api_key is not None else "You haven't api key.")
        ]
    return render_template("account.html", header=header, data=data)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/remake_api")
@login_required
def remake_api():
    db = db_session.create_session()
    u = db.query(User).filter(User.id == current_user.id).first()
    u.api_key = str(uuid.uuid4())
    db.commit()
    return redirect(url_for("account"))


@app.route("/singin", methods=["GET", "POST"])
def singin():
    db = db_session.create_session()

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
    db = db_session.create_session()

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        logging_user = db.query(User).filter(User.name == name).first()
        if logging_user is None:
            flash("There is no such name or password.")
            return render_template("login.html", header=header, form=form)
        password = form.password.data
        if logging_user.check_password(password):
            userlogin = db.query(User).filter(User.name == name).first()
            login_user(userlogin)
            return redirect(url_for('home'))
        else:
            flash("There is no such name or password.")
            return render_template("login.html", header=header, form=form)
    return render_template("login.html", header=header, form=form)


@app.route("/maraphon/<int:id>", methods=["GET", "POST"])
@login_required
def maraphon(id):
    db = db_session.create_session()

    id = int(id)

    maraphon = db.query(Maraphone).filter(Maraphone.id == id).first()

    if not maraphon:
        return abort(404)

    if "add_task" in request.form:
        if maraphon.creator_id != current_user.id:
            return abort(404)

        task = Task(
            main_id=id,
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
            done_users,
            "/" + app.config["UPLOAD_FOLDER"] + "/" + task.image))

    parameters = {
        "id": id,
        "title": maraphon.title,
        "creator": maraphon.creator.name,
        "days": days,
        "is_creator": is_creator,
        "maraphone_name": maraphon.title
    }

    return render_template("maraphon.html", header=header, **parameters)


@app.route("/state/<int:id>", methods=["POST"])
@login_required
def state(id):
    db = db_session.create_session()

    try:
        bstate = json.loads(str(request.data)[2:-1])["state"]
    except Exception:
        return json.dumps(
            {"responsible": False, "error": "jsonfy state error"})

    state = db.query(State).filter(
        State.user_id == current_user.id,
        State.task_id == id).first()

    if not state:
        return json.dumps({"responsible": False, "error": "has not state"})

    if state.task.date != datetime.datetime.today().date():
        return json.dumps(
            {"responsible": False, "state": state.done, "error": "date error"})

    state.done = bstate
    db.commit()

    return json.dumps({"responsible": True, "state": state.done})


@app.route("/maraphon_settigns/<int:id>", methods=["GET", "POST"])
@login_required
def maraphon_settings(id):
    db = db_session.create_session()

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)