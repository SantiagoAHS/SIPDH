from flask import Blueprint,render_template

extra_views = Blueprint('extras', __name__)

@extra_views.route("/terminos")
def terminos():
    return render_template('extras/terminos.html')

@extra_views.route("/politicas")
def politicas():
    return render_template('extras/Politicas.html')

@extra_views.route("/ayudaadmin")
def ayudaadmin():
    return render_template('extras/ayuda.html')

@extra_views.route("/ayudageneral")
def ayudageneral():
    return render_template('extras/ayuda1.html')

@extra_views.route("/ayuda")
def ayuda():
    return render_template('extras/ayuda2.html')


