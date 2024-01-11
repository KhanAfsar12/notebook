from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from flask_marshmallow import Marshmallow
import jwt
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Afsar Khan"
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    notes = db.Column(db.String(200))
    DateTime = db.Column(db.String(39), default=datetime.utcnow())
    admin = db.Column(db.Boolean,default=False)


    def __init__(self, email, password, notes) -> None:
        self.email = email
        self.password= password
        self.notes = notes

with app.app_context():
    db.create_all()


class UserSchema(ma.Schema):
    class Mata:
        fields = ('email', 'password', 'notes', 'DateTime', 'admin')
user_schema = UserSchema()
users_scema = UserSchema(many=True)



def token_required(f):
    @wraps(f)
    def decorator(*args, **kargs):
        token = request.headers['access_token']

        if not token:
            return {"message" : "token not found"}, 401
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        try:
            user = Tracker.query.filter_by(email=user_data['email']).first()
        except:
            return jsonify({'message' : "token is invalid"}), 401
        return f(user, *args, **kargs)
    return decorator


@app.route('/all')
@token_required
def all_user(current_user):
    if not current_user.admin:
        return jsonify({"message" : "you are not authorized"}),401
    users = Tracker.query.all()
    data = user_schema.dump(users)
    return jsonify(data), 201

@app.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    password = generate_password_hash(data['password'])
    print(data)
    trace = Tracker(email = data['email'],notes = data['notes'],password= password)
    db.session.add(trace)
    db.session.commit()
    data = user_schema.dump(trace)
    return jsonify(data), 201



@app.route('/login', methods=['POST'])
def get_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"message" : "Please provide valid details"})
    trace = Tracker.query.filter_by(email=auth.username).first()
    if not trace:
        return jsonify({"message" : "User not found"})
    if check_password_hash(trace.password, auth.password):
        token = jwt.encode({'email' : trace.email, 'exp' : datetime.now(datetime.timezonetimezone.utc)+timedelta(minutes=60)},
                           app.config['SECRET_KEY']
                           )
        return jsonify({"TOKEN" : token})
    return jsonify({'message' : 'could not verify'})

        
        




if __name__ == "__main__":
    app.run(debug=True, port=6000)
