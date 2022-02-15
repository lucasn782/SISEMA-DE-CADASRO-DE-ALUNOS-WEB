import re
from unicodedata import name
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "alunos"

DB_HOST = "ec2-54-235-98-1.compute-1.amazonaws.com"
DB_NAME = "d38uaml6icasp3"
DB_USER = "pdlfrwyhzykixa"
DB_PASS = "47741d44861d5aef64efcd588f9fe1baa954494f0f809d61d9c374caddac17d0"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/')
def Index():
    if 'loggedin' in session:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = 'SELECT * FROM alunos'
        cur.execute(s)
        list_user = cur.fetchall()
        return render_template('index.html', list_user = list_user)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)
        
        cursor.execute('SELECT * FROM usuários WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        if account:
            flash('Essa conta já existe!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('O nome de usuário deve conter apenas caracteres e números!')
        elif not username or not password:
            flash('Por favor, preencha o formulário!')
        else:
            cursor.execute("INSERT INTO usuários (username, password) VALUES (%s,%s)", (username,_hashed_password))
            conn.commit()
            flash('Usuário registrado com sucesso!')
    elif request.method == 'POST':
        flash('Por favor, preencha o formulário!')
        
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        cursor.execute('SELECT * FROM usuários WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            password_rs = account['password']
            print(password_rs)
            if check_password_hash(password_rs, password):
                
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                
                return redirect(url_for('Index'))
            else:
                
                flash('Nome de usuário e/ou senha incorreta!')
        else:
            
            flash('Nome de usuário e/ou senha incorreta!')
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM usuários WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/add_student', methods=['POST'])
def add_student():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        matrícula = request.form['matrícula']
        nome = request.form['nome']
        cpf = request.form['cpf']
        rg = request.form['rg']
        data_nascimento = request.form['data_nascimento']
        nome_do_pai = request.form['nome_do_pai']
        nome_da_mãe = request.form['nome_da_mãe']
        sexo = request.form['sexo']
        email = request.form['email']
        telefone_1 = request.form['telefone_1']
        telefone_2 = request.form['telefone_2']
        endereço = request.form['endereço']
        cur.execute("INSERT INTO alunos (matrícula, nome, cpf, rg, data_nascimento, nome_do_pai, nome_da_mãe, sexo, email, telefone_1, telefone_2, endereço) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (matrícula, nome, cpf, rg, data_nascimento, nome_do_pai, nome_da_mãe, sexo, email, telefone_1, telefone_2, endereço))
        conn.commit()
        flash('Aluno adicionado com sucesso!')
        return redirect(url_for('Index'))

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('SELECT * FROM alunos WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', student = data[0])

@app.route('/update/<id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        matrícula = request.form['matrícula']
        nome = request.form['nome']
        cpf = request.form['cpf']
        rg = request.form['rg']
        data_nascimento = request.form['data_nascimento']
        nome_do_pai = request.form['nome_do_pai']
        nome_da_mãe = request.form['nome_da_mãe']
        sexo = request.form['sexo']
        email = request.form['email']
        telefone_1 = request.form['telefone_1']
        telefone_2 = request.form['telefone_2']
        endereço = request.form['endereço']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE alunos
            SET matrícula = %s,
                nome = %s,
                cpf = %s,
                rg = %s,
                data_nascimento = %s,
                nome_do_pai = %s,
                nome_da_mãe = %s,
                sexo = %s,
                email = %s,
                telefone_1 = %s,
                telefone_2 = %s,
                endereço = %s
            WHERE id = %s
        """, (matrícula, nome, cpf, rg, data_nascimento, nome_do_pai, nome_da_mãe, sexo, email, telefone_1, telefone_2, endereço, id))
        flash('Aluno atualizado com sucesso!')
        conn.commit()
        return redirect(url_for('Index'))

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM alunos WHERE id = {0}'.format(id))
    conn.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('Index'))
if __name__ == "__main__":
    app.run(debug=True)
    
