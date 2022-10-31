from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3

@app.route('/')
def home():
        return render_template('login.html')


@app.route('/course work/databases/templates/creating_account.html')
def signupPage():
        return render_template('creating_account.html')

@app.route('/create')
def create():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""

        CREATE TABLE user (
        username VARCHAR(15) NOT NULL PRIMARY KEY,
        name VARCHAR(12),
        email VARCHAR(30),
        password VARCHAR(20)
        )
        """)
    con.commit()
    con.close()
    return 'tbl created!'


@app.route('/signup', methods=['POST'])
def signup():

        con = sqlite3.connect('userdata.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO user (username, name, email, password)
                        VALUES (?,?,?,?)""",
                        (request.form['usern'],request.form['name'],request.form['mail'],request.form['pass']))
        con.commit()
        con.close()
        return request.form['name'] + ' added'

@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM user WHERE username=? AND password=?""",
                    (request.form['usern'],request.form['pass']))
    match = len(cur.fetchall())
    if match == 0:
        return "Wrong username or password"
    else:
        cur.execute("""SELECT name FROM user WHERE username=?""",
                    (request.form['usern'],))
        name = cur.fetchall()
        name = str(name)
        return render_template('home.html', name=name)


@app.route('/delete')
def delete():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                DROP TABLE user;
        """)

    con.commit()
    con.close()

    return 'tbl deleted'

@app.route('/see')
def see():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM user;
        """)
    rows = cur.fetchall()
    return str(rows)
