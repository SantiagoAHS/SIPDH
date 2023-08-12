from flask import Flask, render_template, request, redirect, url_for, flash, session,make_response,abort
from flask_mysqldb import MySQL
from flask_paginate import Pagination
from datetime import datetime
import mysql.connector
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from flask import Response
import os
from werkzeug.utils import secure_filename


from views.error_views import error_views
from views.home_views import home_views
from views.extra_views import extra_views

    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'My Secret Key'

# Configuración para cargar imágenes
app.config['UPLOAD_FOLDER'] = os.path.abspath('app/static/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'integradora'


mysql = MySQL(app)

app.register_blueprint(error_views)
app.register_blueprint(home_views)
app.register_blueprint(extra_views)


#extra
# Función auxiliar para verificar las extensiones permitidas de archivo

@app.route("/reporte")
def reporte():
    return render_template('extras/reportes.html')

@app.route('/generar_pdf_productos', methods=['GET'])
def generar_pdf_productos():
    # Consulta a la base de datos para obtener los datos de productos
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_producto, nombre, precio, stock, descripcion, fecha_caducidad, categoria, proveedor FROM productos")
    productos_data = cur.fetchall()
    
    # Crear un objeto PDF en orientación horizontal (landscape)
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))
    
    # Contenido del PDF
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Reporte de Productos", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Crear una tabla con los datos de productos
    data = [['ID', 'Nombre', 'Precio', 'Stock', 'Descripción', 'Fecha Caducidad', 'Categoría', 'Proveedor']]
    data.extend(productos_data)
    
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(table)
    
    # Construir el PDF y guardar en el objeto BytesIO
    doc.build(story)
    
    # Regresar el archivo PDF como descarga
    pdf_buffer.seek(0)
    return Response(pdf_buffer, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=reporte_productos.pdf'})

@app.route('/generar_pdf_ventas', methods=['POST'])
def generar_pdf_ventas():
    fecha_inicio = request.form.get('fecha_inicio')

    # Consulta a la base de datos para obtener los datos de ventas
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_venta, fecha_venta, cantidad_prod, total, nombre_empleado FROM venta WHERE fecha_venta >= %s", (fecha_inicio,))
    ventas_data = cur.fetchall()

    # Crear un objeto PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Contenido del PDF
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Reporte de Ventas", styles['Title']))
    story.append(Paragraph(f"Fecha de inicio: {fecha_inicio}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Crear una tabla con los datos de ventas
    data = [['ID Venta', 'Fecha Venta', 'Cantidad Producto', 'Total', 'Nombre Empleado']]
    data.extend(ventas_data)

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(table)

    # Construir el PDF y guardar en el objeto BytesIO
    doc.build(story)

    # Regresar el archivo PDF como descarga
    pdf_buffer.seek(0)
    return Response(pdf_buffer, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=reporte_ventas.pdf'})
#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener las credenciales ingresadas por el usuario
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        acepto_terminos = request.form.get('acepto_terminos')  # Verificar si se marcó la casilla

        if acepto_terminos:

        # Consultar la base de datos para verificar las credenciales
         cur = mysql.connection.cursor()
         cur.execute("SELECT id_empleado, nombre, contraseña, rol FROM empleados WHERE nombre = %s", (nombre_usuario,))
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
        else:
            flash('Debes aceptar los términos y condiciones para acceder.', 'error')

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
        cur.execute("SELECT * FROM productos WHERE nombre LIKE %s", ('%' + search_term + '%',))
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
    cur.execute("SELECT * FROM productos")
    data = cur.fetchall()
    cur.close()

    # Paginar los datos
    page = request.args.get('page', 1, type=int)
    per_page = 14
    data_page = data[(page-1)*per_page:page*per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(data), css_framework='bootstrap4')

    return render_template('administrador/productos.html', producto=data_page, pagination=pagination)

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/insert_po', methods=['POST'])
def insert_po():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        descripcion = request.form['descripcion']
        fecha_caducidad = request.form['fecha_cad']
        proveedor = request.form['proveedor']
        categoria = request.form['categoria']

        # Procesar la imagen cargada
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                # Asegurarse de que el nombre del archivo sea único para evitar colisiones
                filename = secure_filename(imagen.filename)
                imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Crear el directorio de destino si no existe
                os.makedirs(os.path.dirname(imagen_path), exist_ok=True)

                imagen.save(imagen_path)
                # Leer el contenido de la imagen para guardar en la base de datos
                with open(imagen_path, 'rb') as img_file:
                    imagen_blob = img_file.read()

                # Depuración: Verificar si la imagen se carga correctamente
                print("Imagen cargada:", imagen_path)
            else:
                imagen_blob = None
                print("Imagen no cargada debido a la extensión no permitida.")
        else:
            imagen_blob = None
            print("Imagen no proporcionada en el formulario.")

        try:
            # Obtener la conexión a la base de datos y el cursor
            conn = mysql.connection
            cursor = conn.cursor()

            # Insertar el producto en la base de datos utilizando una transacción
            cursor.execute("INSERT INTO productos (nombre, precio, stock, descripcion, fecha_caducidad, categoria, proveedor, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (nombre, precio, stock, descripcion, fecha_caducidad, categoria, proveedor, imagen_blob))
            conn.commit()
            flash("Data Inserted Successfully")
        except mysql.connector.Error as err:
            # Ocurrió un error, hacer rollback de la transacción
            conn.rollback()
            flash(f"Error: {err}")
        finally:
            # Cerrar el cursor (si está abierto) y la conexión
            if cursor:
                cursor.close()

        return redirect(url_for('productos'))

@app.route('/delete_po/<string:id_data>', methods = ['GET'])
def delete_po(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM productos WHERE id_producto=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('productos'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/update_po', methods=['POST'])
def update_po():
    id_data = request.form['id_producto']
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    descripcion = request.form['descripcion']
    fecha_caducidad = request.form['fecha_cad']
    proveedor = request.form['proveedor']
    categoria = request.form['categoria']
    
    # Procesar la imagen actualizada
    imagen_blob = None
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        if imagen.filename != '' and allowed_file(imagen.filename):
            imagen_blob = imagen.read()

            # Guardar la imagen en la carpeta especificada
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imagen.filename))
            imagen.save(imagen_path)

    try:
        # Obtener la conexión a la base de datos y el cursor
        conn = mysql.connection
        cursor = conn.cursor()

        # Actualizar el producto en la base de datos utilizando una transacción
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, stock=%s, descripcion=%s, fecha_caducidad=%s, categoria=%s, proveedor=%s, imagen=%s WHERE id_producto=%s",
                       (nombre, precio, stock, descripcion, fecha_caducidad, categoria, proveedor, imagen_blob, id_data))
        conn.commit()
        flash("Data Updated Successfully")
    except mysql.connector.Error as err:
        # Ocurrió un error, hacer rollback de la transacción
        conn.rollback()
        flash(f"Error: {err}")
    finally:
        # Cerrar el cursor (si está abierto) y la conexión
        if cursor:
            cursor.close()

    return redirect(url_for('productos'))


#Empleados
@app.route('/empleado', methods=['GET', 'POST'])
def empleado():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener los empleados que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM empleados WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/empleado.html', empleado=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los empleados sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM empleados")
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
        rol=request.form['rol']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO empleados (nombre,telefono,correo,direccion,curp,contraseña,rol) VALUES (%s, %s, %s, %s, %s, %s,%s)", 
                    (nombre,telefono,correo,direccion,curp,contraseña,rol))
        mysql.connection.commit()
        return redirect(url_for('empleado'))

@app.route('/delete_e/<string:id_data>', methods = ['GET'])
def delete_e(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM empleados WHERE id_empleado=%s", (id_data,))
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
        rol=request.form['rol']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE empleados SET nombre=%s,telefono=%s ,correo=%s,direccion=%s ,curp=%s ,contraseña=%s, rol=%s WHERE id_empleado=%s",
                    (nombre,telefono,correo,direccion,curp,contraseña,rol,id_data,))
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
        cur.execute("SELECT * FROM proveedores WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/provedor.html', provedor=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los proveedores sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores")
    data = cur.fetchall()
    cur.close()

    return render_template('administrador/provedor.html', provedor=data)

@app.route('/insert_pe', methods = ['POST'])
def insert_pe():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        nombre= request.form['nombre']
        direccion= request.form['direccion']
        telefono= request.form['telefono']
        correo= request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO proveedores (nombre, direccion, telefono, correo) VALUES (%s, %s, %s, %s)",
            (nombre, direccion, telefono, correo))
        mysql.connection.commit()
        return redirect(url_for('provedor'))

@app.route('/delete_pe/<string:id_data>', methods = ['GET'])
def delete_pe(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM proveedores WHERE id_proveedor=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('provedor'))

@app.route('/update_pe', methods=['POST'])
def update_pe():
    id_data = request.form['id_proveedor']
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE proveedores SET nombre=%s, direccion=%s, telefono=%s, correo=%s WHERE id_proveedor=%s",
                (nombre, direccion, telefono, correo, id_data,))
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
        cur.execute("SELECT * FROM categorias WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('administrador/categorias.html', categoria=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todas las categorías sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias")
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
        cur.execute("INSERT INTO  categorias (nombre ,descripcion) VALUES(%s,%s)",(nombre,descripcion))
        mysql.connection.commit()
        return redirect(url_for('categoria'))

@app.route('/delete_cat/<string:id_data>', methods = ['GET'])
def delete_cat(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM categorias WHERE id_categoria=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('categoria'))

@app.route('/update_cat', methods= ['POST'])
def update_cat():
        id_data= request.form['id_categoria']
        nombre= request.form['nombre']
        descripcion= request.form['descripcion']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE categorias SET nombre=%s ,descripcion=%s WHERE id_categoria=%s",
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
            cur.execute("SELECT id_producto, nombre, precio FROM productos WHERE id_producto = %s", (_code,))
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

@app.route('/get_image/<int:id_producto>')
def get_image(id_producto):
    try:
        # Consultar la imagen del producto desde la base de datos
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT imagen FROM productos WHERE id_producto = %s", (id_producto,))
        data = cursor.fetchone()
        cursor.close()

        if data and data[0] is not None:
            # Si se encontró la imagen en la base de datos, retornar la imagen como respuesta
            response = make_response(data[0])
            response.headers['Content-Type'] = 'image/jpeg'  # Ajusta el tipo de contenido según tu caso
            return response
        else:
            # Si no se encontró la imagen, puedes devolver una imagen por defecto o mostrar un mensaje
            # En este ejemplo, simplemente se devuelve una imagen por defecto de error
            with open('path_to_default_image.jpg', 'rb') as img_file:
                default_image = img_file.read()
                response = make_response(default_image)
                response.headers['Content-Type'] = 'image/jpeg'  # Ajusta el tipo de contenido según tu caso
                return response
    except mysql.connector.Error as err:
        # Manejo de errores en caso de problemas con la base de datos
        print(f"Error en la consulta de imagen: {err}")
        return abort(500)  # Respuesta de error en caso de problemas con la base de datos

@app.route('/ventacar', methods=['GET', 'POST'])
def ventacar():
    if request.method == 'POST':
        # Obtener el término de búsqueda ingresado por el usuario
        search_term = request.form['search_term']

        # Consultar la base de datos para obtener los productos que coincidan con el término de búsqueda
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM productos WHERE nombre LIKE %s", ('%' + search_term + '%',))
        data = cur.fetchall()
        cur.close()

        return render_template('empleado/ventacar.html', producto=data, search_term=search_term)

    # Si la solicitud es GET, mostrar todos los productos sin filtrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
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
        nombre_empleado = request.form['nombre']
        fecha_venta = datetime.now().strftime('%Y-%m-%d')
        cantidad_prod = session['all_total_quantity']
        total = session['all_total_price']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO venta(fecha_venta, cantidad_prod, total, nombre_empleado) VALUES (%s, %s, %s, %s)",
            (fecha_venta, cantidad_prod, total, nombre_empleado))
        mysql.connection.commit()

        # Obtener la información de los productos vendidos desde la sesión
        products_sold = session['cart_item']

        # Actualizar el stock de cada producto vendido en la tabla "producto"
        for product_id, product_info in products_sold.items():
            quantity_sold = product_info['quantity']
            cur.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
                        (quantity_sold, product_id))
            mysql.connection.commit()

        # Limpiar el carro de compras después de guardar la orden
        session.clear()

        return render_template('empleado/thank_you.html', 
                               id_empleado=nombre_empleado,
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