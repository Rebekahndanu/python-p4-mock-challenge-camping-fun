#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        camper_data = []
        for camper in campers:
            camper_dict = camper.to_dict(rules=('-signups', ))
            camper_data.append(camper_dict)
        
        return jsonify(camper_data)
    
    # def get(self):
    #     campers = Camper.query.all()
    #     camper_data = []
    #     for camper in campers:
    #         camper_dict = {
    #             "id": camper.id,
    #             "name": camper.name,
    #             "age": camper.age
    #         }
    #         camper_data.append(camper_dict)
    #     return jsonify(camper_data)
    
    def post(self):
        try:
            new_camper = Camper(
                name=request.get_json()['name'],
                age=request.get_json()['age']
            )
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
            

        db.session.add(new_camper)
        db.session.commit()

        return make_response(new_camper.to_dict(), 200)

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()

        if camper:
            return make_response(camper.to_dict(), 200)

        else:
            return make_response({"error": "Camper not found"}, 404)
        
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        
        if camper:
            try:
                for attr in request.json:
                    setattr(camper, attr, request.json[attr])
                
                db.session.commit()
                response_body = camper.to_dict(rules=('-signups',))
                return make_response(response_body, 202)
            except:
                response_body = {
                    "errors": ["validation errors"]
                }
                return make_response(response_body, 400)
        else:
            response_body = {
                "error": "Camper not found"
            }
            return make_response(response_body, 404)
        
class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        activity_data = []
        for activity in activities:
            activity_dict = {
                "id": activity.id,
                "name": activity.name,
                "difficulty": activity.difficulty
            }
            activity_data.append(activity_dict)
        return jsonify(activity_data)

class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()

        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response({"error": "Activity not found"}, 404)

class Signups(Resource):
    def post(self):

        data = request.get_json()

        try:
            new_signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time'],
            )

            db.session.add(new_signup)
            db.session.commit()

            return make_response(new_signup.to_dict(), 201)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    

api.add_resource(Campers, '/campers')
api.add_resource(CamperById, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityById, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
