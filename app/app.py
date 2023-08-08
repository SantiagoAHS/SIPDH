from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_paginate import Pagination
from datetime import datetime
import mysql.connector


from views.error_views import error_views
from views.home_views import home_views
from views.extra_views import extra_views
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'My Secret Key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'integradora'


mysql = MySQL(app)

app.register_blueprint(error_views)
app.register_blueprint(home_views)
app.register_blueprint(extra_views)


#extra
@app.route("/reporte")
def reporte():
    return render_template('extras/reportes.html')

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener las credenciales ingresadas por el usuario
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']

        # Consultar la base de datos para verificar las credenciales
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_empleado, nombre, contraseña, rol FROM empleado WHERE nombre = %s", (nombre_usuario,))
        usuario = cur.fetchone()
        cur.close()

        if usuario:
            id_empleado, nombre, contraseña_db, rol = usuario
            if contraseña == contraseña_db:
                # Las credenciales son válidas, guardar el rol en la sesión
                session['rol'] = rol
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña incorrecta. Inténtalo de nuevo.', 'error')
        else:
            flash('Usuario no encontrado. Inténtalo de nuevo.', 'error')

    return render_template('extras/login.html')

@app.route('/dashboard')
def dashboard():
    # Verificar si el usuario ha iniciado sesión y tiene un rol asignado
    if 'rol' in session:
        rol = session['rol']
        if rol == 'admin':
            # Redirigir a la página del administrador
            return render_template('home/home.html')
        elif rol == 'general':
            # Redirigir a la página del usuario general
            return render_template('home/emp2.html')
    else:
        # Si el usuario no ha iniciado sesión, redirigir al inicio de sesión
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Eliminar la sesión activa y redireccionar al inicio de sesión
    session.clear()
    return render_template('home/inicio.html')

#Venta
@app.route('/registrosventa', methods=['GET', 'POST'])
def registrosventa():
    if request.method == 'POST':
        # Obtener la fecha ingresada por el usuario en el formulario de búsqueda
        fecha_venta = request.form['fecha_venta']

        # Convertir la fecha ingresada a un objeto datetime
        try:
            fecha_venta = datetime.strptime(fecha_venta, '%Y-%m-%d').date()
        except ValueError:
            flash('Fecha inválida. Ingrese una fecha en formato AAAA-MM-DD.', 'error')
            return redirect(url_for('registrosventa'))

        # Consultar la base de datos para obtener las ventas que coincidan con la fecha ingresada
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM venta WHERE fecha_venta = %s", (fecha_venta,))
        data = cur.fetchall()
        cur.close()

        # Paginar los datos
        page = request.args.get('page', 1, type=int)
        per_page = 15
        data_page = data[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')

        return render_template('empleado/registroventa.html', venta=data, pagination=pagination, fecha_venta=fecha_venta)

    # Si la solicitud es GET, mostrar todas las ventas sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM venta")
    data = cur.fetchall()
    cur.close()

    # Paginar los datos
    page = request.args.get('page', 1, type=int)
    per_page = 15
    data_page = data[(page-1)*per_page:page*per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')

    return render_template('empleado/registroventa.html', venta=data_page, pagination=pagination)

#Productos
@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener los productos que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM producto WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        # Paginar los datos
        page = request.args.get('page', 1, type=int)
        per_page = 15
        data_page = data[(page-1)*per_page:page*per_page]
        pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')

        return render_template('administrador/productos.html', producto=data_page, pagination=pagination, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los productos sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM producto")
    data = cur.fetchall()
    cur.close()

    # Paginar los datos
    page = request.args.get('page', 1, type=int)
    per_page = 14
    data_page = data[(page-1)*per_page:page*per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')

    return render_template('administrador/productos.html', producto=data_page, pagination=pagination)

@app.route('/insert_po', methods = ['POST'])
def insert_po():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre= request.form['nombre']
        precio= request.form['precio']
        stock= request.form['stock']
        descripcion= request.form['descripcion']
        fecha_cad= request.form['fecha_cad']
        id_provedor= request.form['id_provedor']
        id_categoria= request.form['id_categoria']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO producto (nombre,precio,stock,descripcion,fecha_cad,id_provedor,id_categoria) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (nombre,precio,stock,descripcion,fecha_cad,id_provedor,id_categoria))
        mysql.connection.commit()
        return redirect(url_for('productos'))

@app.route('/delete_po/<string:id_data>', methods = ['GET'])
def delete_po(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM producto WHERE id_producto=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('productos'))

@app.route('/update_po', methods= ['POST'])
def update_po():
        id_data= request.form['id_producto']
        nombre= request.form['nombre']
        precio= request.form['precio']
        stock= request.form['stock']
        descripcion= request.form['descripcion']
        fecha_cad= request.form['fecha_cad']
        id_provedor= request.form['id_provedor']
        id_categoria= request.form['id_categoria']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE producto SET nombre=%s,precio=%s ,stock=%s ,descripcion=%s ,fecha_cad=%s ,id_provedor=%s ,id_categoria=%s WHERE id_producto=%s",
                    (nombre,precio,stock,descripcion,fecha_cad,id_provedor,id_categoria,id_data,))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('productos'))

#Empleados
@app.route('/empleado', methods=['GET', 'POST'])
def empleado():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener los empleados que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM empleado WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/empleado.html', empleado=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los empleados sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM empleado")
    data = cur.fetchall()
    cur.close()

    return render_template('administrador/empleado.html', empleado=data)

@app.route('/insert_e', methods = ['POST'])
def insert_e():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre= request.form['nombre']
        telefono= request.form['telefono']
        correo= request.form['correo']
        direccion= request.form['direccion']
        curp= request.form['curp']
        contraseña= request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO empleado (nombre,telefono,correo,direccion,curp,contraseña) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (nombre,telefono,correo,direccion,curp,contraseña))
        mysql.connection.commit()
        return redirect(url_for('empleado'))

@app.route('/delete_e/<string:id_data>', methods = ['GET'])
def delete_e(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM empleado WHERE id_empleado=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('empleado'))

@app.route('/update_e', methods= ['POST'])
def update_e():
        id_data= request.form['id_empleado']
        nombre= request.form['nombre']
        telefono= request.form['telefono']
        correo= request.form['correo']
        direccion= request.form['direccion']
        curp= request.form['curp']
        contraseña= request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE empleado SET nombre=%s,telefono=%s ,correo=%s,direccion=%s ,curp=%s ,contraseña=%s WHERE id_empleado=%s",
                    (nombre,telefono,correo,direccion,curp,contraseña,id_data,))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('empleado'))

#Provedores
@app.route('/provedor', methods=['GET', 'POST'])
def provedor():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']
        
        # Consultar la base de datos para obtener los proveedores que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM provedor WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/provedor.html', provedor=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los proveedores sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM provedor")
    data = cur.fetchall()
    cur.close()

    return render_template('administrador/provedor.html', provedor=data)

@app.route('/insert_pe', methods = ['POST'])
def insert_pe():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre= request.form['nombre']
        telefono= request.form['telefono']
        correo= request.form['correo']
        direccion= request.form['direccion']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO provedor (nombre,telefono,correo,direccion) VALUES (%s, %s, %s, %s)", 
                    (nombre,telefono,correo,direccion))
        mysql.connection.commit()
        return redirect(url_for('provedor'))

@app.route('/delete_pe/<string:id_data>', methods = ['GET'])
def delete_pe(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM provedor WHERE id_provedor=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('provedor'))

@app.route('/update_pe', methods= ['POST'])
def update_pe():
        id_data= request.form['id_provedor']
        nombre= request.form['nombre']
        telefono= request.form['telefono']
        correo= request.form['correo']
        direccion = request.form['direccion']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE provedor SET nombre=%s ,telefono=%s ,correo=%s, direccion=%s WHERE id_provedor=%s",
                    (nombre,telefono,correo,direccion,id_data,))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('provedor'))

#Categoria
@app.route('/categoria', methods=['GET', 'POST'])
def categoria():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener las categorías que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM categoria WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/categorias.html', categoria=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todas las categorías sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categoria")
    data = cur.fetchall()
    cur.close()

    return render_template('administrador/categorias.html', categoria=data)

@app.route('/insert_cat', methods = ['POST'])
def insert_cat():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre= request.form['nombre']
        descripcion= request.form['descripcion']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO  categoria (nombre ,descripcion) VALUES(%s,%s)",(nombre,descripcion))
        mysql.connection.commit()
        return redirect(url_for('categoria'))

@app.route('/delete_cat/<string:id_data>', methods = ['GET'])
def delete_cat(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categoria WHERE id_categoria=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('categoria'))

@app.route('/update_cat', methods= ['POST'])
def update_cat():
        id_data= request.form['id_categoria']
        nombre= request.form['nombre']
        descripcion= request.form['descripcion']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE categoria SET nombre=%s ,descripcion=%s WHERE id_categoria=%s",
                    (nombre,descripcion,id_data,))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('categoria'))

#Venta
@app.route('/add', methods=['POST'])
def add_product_to_cart():
    try:
        _quantity = int(request.form['quantity'])
        _code = int(request.form['code'])

        # Validar los valores recibidos
        if _quantity and _code and request.method == 'POST':

            cur = mysql.connection.cursor()
            cur.execute("SELECT id_producto, nombre, precio FROM producto WHERE id_producto = %s", (_code,))
            data = cur.fetchone()

            if not data:
                return 'Producto no encontrado'

            product_id = data[0]
            nombre_producto = data[1]
            precio_producto = float(data[2])

            # Agregar el producto al carro de compras
            itemArray = {
                product_id: {
                    'nombre': nombre_producto,  # Aquí se debe usar 'nombre' en lugar de 'name'
                    'id_producto': product_id,  # Aquí se debe usar 'id_producto' en lugar de 'code'
                    'quantity': _quantity,
                    'precio': precio_producto,  # Aquí se debe usar 'precio' en lugar de 'price'
                    'total_price': _quantity * precio_producto
                }
             }
            all_total_quantity = 0
            all_total_price = 0

            session.modified = True
            if 'cart_item' in session:
                if str(product_id) in session['cart_item']:
                    # Si el producto ya está en el carro, actualiza la cantidad y el precio total
                    old_quantity = session['cart_item'][str(product_id)]['quantity']
                    total_quantity = old_quantity + _quantity
                    session['cart_item'][str(product_id)]['quantity'] = total_quantity
                    session['cart_item'][str(product_id)]['total_price'] = total_quantity * precio_producto
                else:
                    # Si el producto no está en el carrito, agrégalo al diccionario 'cart_item'
                    session['cart_item'][str(product_id)] = {
                        'nombre': nombre_producto,
                        'id_producto': product_id,
                        'quantity': _quantity,
                        'precio': precio_producto,
                        'total_price': _quantity * precio_producto
                    }

                # Recalcula los valores totales después de agregar el producto al carrito
                for item_id, item_data in session['cart_item'].items():
                    all_total_quantity += item_data['quantity']
                    all_total_price += item_data['total_price']

            else:
                # Si no hay carro de compras, crea uno y agrega el primer producto
                session['cart_item'] = itemArray
                all_total_quantity = _quantity
                all_total_price = _quantity * precio_producto

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('.ventacar'))

        else:
            return 'Valores incorrectos o método de solicitud inválido'

    except Exception as e:
        return 'Error: ' + str(e)

        

@app.route('/ventacar', methods=['GET', 'POST'])
def ventacar():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener los productos que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM producto WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('empleado/ventacar.html', producto=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los productos sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM producto")
    data = cur.fetchall()
    cur.close()

    return render_template('empleado/ventacar.html', producto=data)
 
@app.route('/empty')
def empty_cart():
 try:
  session.clear()
  return redirect(url_for('.ventacar'))
 except Exception as e:
  print(e)
 
@app.route('/delete_pre/<string:code>')
def delete_pre(code):
 try:
  all_total_price = 0
  all_total_quantity = 0
  session.modified = True
   
  for item in session['cart_item'].items():
   if item[0] == code:    
    session['cart_item'].pop(item[0], None)
    if 'cart_item' in session:
     for key, value in session['cart_item'].items():
      individual_quantity = int(session['cart_item'][key]['quantity'])
      individual_price = float(session['cart_item'][key]['total_price'])
      all_total_quantity = all_total_quantity + individual_quantity
      all_total_price = all_total_price + individual_price
    break
   
  if all_total_quantity == 0:
   session.clear()
  else:
   session['all_total_quantity'] = all_total_quantity
   session['all_total_price'] = all_total_price
   
  return redirect(url_for('.ventacar'))
 except Exception as e:
  print(e)

#Checkout
@app.route('/checkout', methods=['GET'])
def checkout():
    return render_template('empleado/checkout.html', cart=session['cart_item'], total_quantity=session['all_total_quantity'], total_price=session['all_total_price'])


@app.route('/save_order', methods=['POST'])
def save_order():
    try:
        id_empleado = request.form['id_empleado']
        fecha_venta = datetime.now().strftime('%Y-%m-%d')
        cantidad_prod = session['all_total_quantity']
        total = session['all_total_price']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO venta (id_empleado, fecha_venta, cantidad_prod, total) VALUES (%s, %s, %s, %s)",
            (id_empleado, fecha_venta, cantidad_prod, total))
        mysql.connection.commit()

        # Obtener la información de los productos vendidos desde la sesión
        products_sold = session['cart_item']

        # Actualizar el stock de cada producto vendido en la tabla "producto"
        for product_id, product_info in products_sold.items():
            quantity_sold = product_info['quantity']
            cur.execute("UPDATE producto SET stock = stock - %s WHERE id_producto = %s",
                        (quantity_sold, product_id))
            mysql.connection.commit()

        # Limpiar el carro de compras después de guardar la orden
        session.clear()

        return render_template('empleado/thank_you.html', 
                               id_empleado=id_empleado,
                               fecha_venta=fecha_venta,
                               cantidad_prod=cantidad_prod,
                               total=total)
    except Exception as e:
        # Manejar cualquier error de inserción en la base de datos
        print(e)
        return "Error al guardar la orden. Inténtalo de nuevo."
   
@app.route('/thank_you')
def thank_you():
    # Aquí puedes mostrar un mensaje de agradecimiento o confirmación de la compra después de que se haya procesado la venta
    return render_template('empleado/thank_you.html')

def array_merge( first_array , second_array ):
 if isinstance( first_array , list ) and isinstance( second_array , list ):
  return first_array + second_array
 elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
  return dict( list( first_array.items() ) + list( second_array.items() ) )
 elif isinstance( first_array , set ) and isinstance( second_array , set ):
  return first_array.union( second_array )
 return False

if __name__ == '__main__':
    app.run(debug=True)