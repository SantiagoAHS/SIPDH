from flask import Blueprint,render_template

extra_views = Blueprint('extras', __name__)

@extra_views.route("/terminos")
def terminos():
    return render_template('extras/terminos.html')

@extra_views.route("/politicas")
def politicas():
    return render_template('extras/Politicas.html')


