from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, JWTManager, jwt_required
from flask_marshmallow import Marshmallow



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Afsar Khan"
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    notes = db.Column(db.String(200))
    DateTime = db.Column(db.String(39))

with app.app_context():
    db.create_all()


class Schema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password', 'notes', 'DateTime')
schema = Schema()
schemas = Schema(many=True)





@app.route('/process', methods=['POST'])
def post():
    mail = request.json['email']
    pwd = request.json['password']
    note = request.json['notes']
    if not mail or not pwd or not note:
        return {"message": "Credentials are required!"}
    time = datetime.now().strftime("%Y-%M-%D %H:%M:%S")
    if Tracker.query.filter_by(email=mail).first():
        return {"message": "User already taken"}
    new_user = Tracker(email=mail, password=pwd, notes=note, DateTime=time)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "Congratulations!!! Your account has been created successfully"}


@app.route('/login', methods=['POST'])
@jwt_required() 
def login():
    try:
        mail = request.json['email']
        pwd = request.json['password']
        trace = Tracker.query.filter_by(email=mail).first()
        if trace and trace.password == pwd:
            access_token = create_access_token(identity=trace.id)
            return {"access token":access_token}, 200
        return {"message" : "Invalid credentials"}, 401
    except jwt.ExpiredSignatureError:
        return {"message": "Token has expired"}, 401
    except Exception as e:
        return {"message": "An error occurred during login"}, 500

@app.route('/secure', methods=['GET'])
@jwt_required()
def sec():
    current_user_id = get_jwt_identity()
    return {"message" : f"hello user {current_user_id} you access the protected resource"}



@app.route('/get', methods=['GET'])
@jwt_required()
def ret():
    trace = Tracker.query.all()
    data = []
    for i in trace:
        a = {'id': i.id, 'email':i.email, 'password':i.password, 'notes':i.notes, 'DateTime':i.DateTime}
        data.append(a)
    return jsonify(data)


@app.route('/only/<id>', methods=['GET'])
@jwt_required()
def get(id):
    trace = Tracker.query.get(id)
    if trace:
        data = {'id':trace.id, 'email':trace.email, 'password':trace.password, 'notes':trace.notes, 'DateTime':trace.DateTime}
        return jsonify(data)
    return {'message' : 'id is not found'},404



@app.route('/update/<id>' , methods = ['PUT'])
# @jwt_required()
def update(id):
    trace = Tracker.query.get(id)
    if trace:
        new_password = request.json['password'] 
        # new_notes = request.json['notes']
        if new_password is not None:
            trace.password=new_password
            db.session.commit()
            return {"message" : "Item updated successfully"}
        else:
            return {"message" : "there is no valid data for updation"}
    return {"message" : "Item is not present"}, 404


@app.route('/delete/<id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    remove = Tracker.query.get(id)
    if remove:
        db.session.delete(remove)
        db.session.commit()
        return {"message" : f'Item of {remove} deleted successfully'}
    else:
        return {"message" : "your id is wrong"}






if __name__=="__main__":
    app.run(debug=True)