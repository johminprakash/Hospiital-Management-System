from flask import Flask,render_template,request
from app.routes.admin_logic import admin_logic_bp
from app.routes.doctor_logic import doctor_logic_bp
from app.routes.patient_logic import patient_logic_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'devkey123'

    @app.route('/')
    def home():
        return render_template("home.html")

    app.register_blueprint(admin_logic_bp)
    app.register_blueprint(doctor_logic_bp)
    app.register_blueprint(patient_logic_bp)

    @app.route("/helloworld")
    def helloworld():
        return render_template("helloworld.html")

    
    return app
