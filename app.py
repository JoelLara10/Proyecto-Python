from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import bcrypt

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por algo seguro

# Configuración de MySQL
DB_HOST = 'localhost'  # O tu host de Hostinger
DB_USER = 'root'  # Tu usuario de MySQL
DB_PASS = ''  # Tu contraseña de MySQL
DB_NAME = 'ineo_db'  # Nombre de la BD


def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    role = session['role']
    menu_options = []

    if role == 'admin':
        menu_options = ['Administrativo', 'Médico', 'Estudios', 'Configuración']
    elif role == 'medico':
        menu_options = ['Pacientes', 'Exámenes', 'Registros']  # Ejemplo para médico
    # Agrega más roles según necesites

    return render_template('dashboard.html', role=role, menu_options=menu_options)


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)