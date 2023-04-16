from flask_restful import Api, Resource, reqparse
from flask import jsonify, abort
from datetime import date

from data.maraphones import Maraphone
from data.tasks import Task

api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument("api_key", required=True, type=str)


class MaraphoneApi(Resource):
    def get(self, id):
        args = api_key_parser.parse_args()

        db = db_session.create_session()
        m = db.query(Maraphone).filter(Maraphone.id == id).first()
        if m is None:
            return abort(404, message="maraphone not found")
        return jsonify({"maraphone": m.to_dict()})
    

class TasksListApi(Resource):
    def get(self, maraphone_id):
        args = api_key_parser.parse_args()

        db = db_session.create_session()

        m = db.query(Maraphone).filter(Maraphone.id == id).first()
        if m is None:
            return abort(404, message="maraphone not found")

        t = db.query(Task).filter(Task.main_id == maraphone_id).all()
        return jsonify({"tasks": [i.to_dict() for i in t]})


parser = reqparse.RequestParser()
parser.add_argument("maraphone_id", required=True, type=int)
parser.add_argument("name", required=True, type=str)
parser.add_argument("date", required=True, type=date)
parser.add_argument("description", required=True, type=str)
parser.add_argument("api_key", required=True, type=str)


class TasksApi(Resource):
    def get(self, task_id):
        db = db_session.create_session()
        args = api_key_parser.parse_args()

        t = db.query(Task).filter(Task.id == task_id).first()
        if t is None:
            return abort(404, message="task not found")
        
        return jsonify(t.to_dict())
    
    def post(self):
        args = parser.parse_args()
        db = db_session.create_session()

        m = db.query(Maraphone).filter(Maraphone.id == id).first()
        if m is None:
            return abort(404, message="maraphone not found")

        t = Task(
            main_id=args.maraphone_id,
            name=args.name,
            date=args.date,
            description=args.description)
        
        db.add(t)
        db.commit()