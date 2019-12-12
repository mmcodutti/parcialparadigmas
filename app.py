import csv
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from forms import LoginForm, SaludarForm, RegistrarForm, AltaNuevoCliente, FiltroFecha, FiltroEdad, FiltroPais

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'aca va cualquier cosa que sirva para hashear'

#carga en una lista el archivo de clientes y lo devuelve
def ListaCSV():
    with open('clientes.csv', 'r', encoding="UTF-8") as archivoclientes:
        leearch = csv.reader(archivoclientes)
        archlist= list(leearch)
    return archlist

def encabezado(tabla):
    return tabla[0]

def cuerpo(tabla):
    del tabla[0]
    return tabla   

def listapaises(tabla, pais):
    listaprevia=list()
    for i in range(len(tabla)-1):
        aux=tabla[i][3]
        if (pais.lower() in aux.lower()):
            listaprevia.append(aux)
    return sorted(list(set(listaprevia)))                

def filtrado(tabla, que, dedonde):
    if que=='a':
        clientesfiltrados=filter(lambda x: x[5]<dedonde, tabla)
    elif que=='m':
        clientesfiltrados=filter(lambda x: x[5]==dedonde, tabla)
    elif que=='p':
        clientesfiltrados=filter(lambda x: x[5]>dedonde, tabla)
    elif que=='j':
        clientesfiltrados=filter(lambda x: int(x[1])<int(dedonde), tabla)
    elif que=='i':
        clientesfiltrados=filter(lambda x: int(x[1])==int(dedonde), tabla)
    elif que=='v':
        clientesfiltrados=filter(lambda x: int(x[1])>int(dedonde), tabla)
    elif que=='n':
        clientesfiltrados=filter(lambda x: x[3]==dedonde, tabla)
    return list(clientesfiltrados)
#
#
# acá comienzan las URL
#
@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow())

@app.route('/filt-pais', methods=['GET', 'POST'])
def filtpais():
    if 'username' in session:
        formulario=FiltroPais()
        if formulario.validate_on_submit():
            clientesafiltrar=ListaCSV()
            cabeza=encabezado(clientesafiltrar)
            tabladeclientesafiltrar=cuerpo(clientesafiltrar)
            opciones=listapaises(tabladeclientesafiltrar, formulario.pais.data)
            return render_template('selepais.html', opciones=opciones)
        return render_template('ffecha.html', formulario=formulario, filtro="fecha")
    else:
        return redirect(url_for('ingresar'))

@app.route('/filt-pais/pais/<pais>', methods=['GET'])
def filtrarpais(pais):
    if 'username' in session:
        clientesafiltrar=ListaCSV()
        cabeza=encabezado(clientesafiltrar)
        tabladeclientesafiltrar=cuerpo(clientesafiltrar)
        tablafiltrada=filtrado(tabladeclientesafiltrar, 'n', pais)
        cantcli=len(tablafiltrada)
        return render_template('clientes.html', cantidad=cantcli, listacli=tablafiltrada, encabezado=cabeza, totfil="filtrados")
    else:
        return redirect(url_for('ingresar'))
    
@app.route('/filt-fecha', methods=['GET', 'POST'])
def filtfecha():
    if 'username' in session:
        formulario=FiltroFecha()
        if formulario.validate_on_submit():
            clientesafiltrar=ListaCSV()
            cabeza=encabezado(clientesafiltrar)
            tabladeclientesafiltrar=cuerpo(clientesafiltrar)
            tablafiltrada=filtrado(tabladeclientesafiltrar, formulario.seleccionfecha.data, formulario.fecha.data)
            cantcli=len(tablafiltrada)
            return render_template('clientes.html', cantidad=cantcli, listacli=tablafiltrada, encabezado=cabeza, totfil="filtrados") 
        return render_template('ffecha.html', formulario=formulario, filtro="fecha")
    else:
        return redirect(url_for('ingresar'))

@app.route('/filt-edad', methods=['GET', 'POST'])
def filtedad():
    if 'username' in session:
        formulario=FiltroEdad()
        if formulario.validate_on_submit():
            clientesafiltrar=ListaCSV()
            cabeza=encabezado(clientesafiltrar)
            tabladeclientesafiltrar=cuerpo(clientesafiltrar)
            tablafiltrada=filtrado(tabladeclientesafiltrar, formulario.seleccionfecha.data, formulario.fecha.data)
            cantcli=len(tablafiltrada)
            return render_template('clientes.html', cantidad=cantcli, listacli=tablafiltrada, encabezado=cabeza, totfil="filtrados") 
        return render_template('ffecha.html', formulario=formulario, filtro="edad")
    else:
        return redirect(url_for('ingresar'))

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'username' in session:
        tabla=ListaCSV()
        cabeza=encabezado(tabla)
        cli=cuerpo(tabla)
        cantcli=len(tabla)
        return render_template('clientes.html', cantidad=cantcli, listacli=cli, encabezado=cabeza, totfil="totales") 
    else:
        return redirect(url_for('ingresar'))
        
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

@app.route('/altacliente', methods=['GET', 'POST'])
def altacliente():
    formulario=AltaNuevoCliente()
    if formulario.validate_on_submit():
        with open('clientes.csv', 'a+') as archivo:
            archclientes_csv= csv.writer(archivo)
            registro=[formulario.nombre.data, str(formulario.edad.data), formulario.direccion.data, formulario.pais.data, formulario.documento.data, formulario.fechaalta.data, formulario.correo.data, formulario.trabajo.data]
            archclientes_csv.writerow(registro)
        flash('Cliente agregado')
        return redirect(url_for('clientes'))
    return render_template('altaclientes.html', form=formulario)    

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
