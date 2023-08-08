from flask import Blueprint,render_template

home_views = Blueprint('home', __name__)

@home_views.route("/")
@home_views.route("/inicio")
def inicio():
    return render_template('home/inicio.html')

@home_views.route("/home")
def home():
    return render_template('home/home.html')

@home_views.route("/emp2")
def emp2():
    return render_template('home/emp2.html')