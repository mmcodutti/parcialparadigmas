import csv
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from forms import LoginForm, SaludarForm, RegistrarForm

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'aca va cualquier cosa que sirva para hashear'

#carga en una lista el archivo de clientes y lo devuelve
def ListaCSV():
    with open('clientes.csv', 'r') as archivoclientes:
        leearch = csv.reader(archivoclientes)
        archlist= list(leearch)
    return archlist

@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow())



@app.route('/clientes', methods=['GET'])
def clientes():
    if 'username' in session:
        tabla=ListaCSV()
        cantcli=len(tabla)-1
        cabeza=tabla[0]
        del tabla [0]     
        return render_template('clientes.html', cantidad=cantcli, listacli=tabla, encabezado=cabeza) 
    else:
        formulario = LoginForm()
        if formulario.validate_on_submit():
            with open('usuarios') as archivo:
                archivo_csv = csv.reader(archivo)
                registro = next(archivo_csv)
                while registro:
                    if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                        flash('Bienvenido')
                        session['username'] = formulario.usuario.data
                        return render_template('ingresado.html')
                    registro = next(archivo_csv, None)
                else:
                    flash('Revisá nombre de usuario y contraseña')
                    return redirect(url_for('ingresar'))
        return render_template('login.html', formulario=formulario)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    flash('Bienvenido')
                    session['username'] = formulario.usuario.data
                    return render_template('ingresado.html')
                registro = next(archivo_csv, None)
            else:
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        if formulario.password.data == formulario.password_check.data:
            with open('usuarios', 'a+') as archivo:
                archivo_csv = csv.writer(archivo)
                registro = [formulario.usuario.data, formulario.password.data]
                archivo_csv.writerow(registro)
            flash('Usuario creado correctamente')
            return redirect(url_for('ingresar'))
        else:
            flash('Las passwords no matchean')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return redirect(url_for('index'))

@app.route('/sobre', methods=['GET'])
def sobre():
    return render_template('sobre.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
