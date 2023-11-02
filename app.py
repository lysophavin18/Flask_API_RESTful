from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import click
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret' # change this IRL
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'c4fb061692c85d'
app.config['MAIL_PASSWORD'] = 'dcb6005a25083d'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False



db =SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)



@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():

    sophavin = Planets(planets_name='Sophavin',
                      planets_type='Class D',
                      home_star='Sol',
                      mass=3.57387,
                      raduis=1516,
                      disMailtance=35.7726)


    lay = Planets(planets_name='lay',
                      planets_type='Class E',
                      home_star='Sol',
                      mass=8.57387,
                      raduis=1516,
                      distance=67.7726)

    reaksa = Planets(planets_name='raksa',
                      planets_type='Class F',
                      home_star='Sol',
                      mass=5.567387,
                      raduis=1416,
                      distance=99.7726)
    
    db.session.add(sophavin)
    db.session.add(lay)
    db.session.add(reaksa)
    
    test_user = User(first_name='Sophavin',
                     last_name='Ly',
                     email='ly.sophavin@gmail.com',
                     password='P@ssword')
    
    db.session.add(test_user)
    db.session.commit()
    print('Database seeded!')

app.debug = True

@app.route('/')
def hello_world():
    return 'Hello world'


@app.route('/dog')
def dog():
    return jsonify(message='Dog'), 200

@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age<18:
        return jsonify(message='Sorry'+ name +',you are not old enough.'), 401
    else: 
        return jsonify(message='Welcome'+ name +',you are old enought!')

@app.route('/url_varriable/<string:name>/<int:age>')
def url_varriable(name: str, age:int):
    if age<18:
        return jsonify(message='Sorry'+ name +',you are not old enough.'), 401
    else: 
        return jsonify(message='Welcome'+ name +',you are old enought!')



@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planets.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)




@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message= "User created successfully."), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']  
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Bad email or password"), 401 


@app.route('/retrive_password/<string:email>' ,methods=['GET'])
def retrive_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message('you plane api password '+ user.password,
                       sender="admin@plane-api.com",
                       recipients=[email] )
 
        mail.send(msg)
        return jsonify(mesange='password sent to ' + email)
    else:
        return jsonify(message='That email doesnt exist'), 401     


@app.route('/planet_details/<int:planets_id>', methods=['GET'])
def planet_details(planets_id: int):
    planet = Planets.query.filter_by(planets_id=planets_id).first()
    if planet:
        result = planet_schema.dump(planet)  # Use singular form
        return jsonify(result)
    else:
        return jsonify(message="That planet does not exist"), 404


@app.route('/add_planet', methods=['POST'])
def add_planet():
    planet_name = request.form.get('planets_name')
    test = Planets.query.filter_by(planets_name=planet_name).first()
    if test:
        return jsonify(message="There is already a planet by that name"), 409
    else:
        planets_type = request.form.get('planets_type')
        home_star = request.form.get('home_star')
        mass = float(request.form.get('mass'))
        
        
        raduis_str = request.form.get('raduis')
        if raduis_str is not None:
            raduis = float(raduis_str)
        else:
            raduis = None  

        distance = float(request.form.get('distance'))

        new_planet = Planets(
            planets_name=planet_name,
            planets_type=planets_type,
            home_star=home_star,
            mass=mass,
            raduis=raduis,
            distance=distance
        )

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="You added a planet"), 201







# database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planets(db.Model):
    __tablename__ = 'planets'
    planets_id = Column(Integer, primary_key=True)
    planets_name = Column(String)
    planets_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    raduis = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')



class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planets_id', 'planets_name', 'planets_type', 'home_star', 'mass', 'raduis', 'distance')



user_schema = UserSchema()
users_schema = UserSchema(many=True)


planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)



if __name__ == '__main__':
    app.run()