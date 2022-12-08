from flask import Flask, render_template, request, session, url_for, redirect
app = Flask(__name__)
import sqlite3

app.secret_key = 'LOL_SECRET_KEY'

#NOTES
#IF NOT MUCH TIME LEFT AND USING API IS TOO COMPLICATED, INSERT 7-10 GAMES YOURSELF AND WORK WITH IT


#PAGES

@app.route('/')
def login_page():
        return render_template('login.html')




@app.route('/creating_account')
def signupPage():
        return render_template('creating_account.html')




@app.route('/signup', methods=['GET','POST'])
def signup():

        # creates an account for the user, the validation is done client side for now#
        # if it is successful, it redirects the user to 'questionnaire' page 

        con = sqlite3.connect('userdata.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO user (username, name, email, password)
                        VALUES (?,?,?,?)""",
                        (request.form['usern'],request.form['name'],request.form['mail'],request.form['pass']))
        con.commit()
        cur.execute("""INSERT INTO settings (username, theme, fontsize)
                        VALUES (?,?,?)""",
                        (request.form['usern'], '1', '25'))
        con.commit()
        con.close()

        session['user'] = request.form['usern']

        return redirect(url_for('interest_test'))



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
        session['user'] = request.form['usern']

        return redirect(url_for('home'))




@app.route('/home')
def home():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()

    if session.get('user') == None:
        return render_template('home.html', name="Welcome, idiot")
    else:
        cur.execute("""SELECT name FROM user WHERE username=?""",
                        (session['user'],))
        name = cur.fetchall()
        if session['user'] == 'albert_dev':
            return render_template('home.html', tool="<a href=dev_board id=board>Dev board</a>",
                                                name="Welcome, " + name[0][0])
        else:
            return render_template('home.html', name="Welcome, " + name[0][0])




@app.route('/tech-support', methods=['GET', 'POST'])
def tech_support():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM messages WHERE username=?""",
        (session['user'],))
    match = len(cur.fetchall())
    if match != 0:
            return render_template('tech-support.html', match=1)

    elif request.method == 'POST':
        cur.execute("""INSERT INTO messages (username, reason, text)
                        VALUES (?,?,?)""",
                        (session['user'], request.form['reason'], request.form['text']))
        con.commit()
        con.close()

        return render_template('tech-support.html', match=1)

    else:

        return render_template('tech-support.html')




@app.route('/catalogue')
def catalogue():
    return render_template('catalogue.html')




@app.route('/settings', methods=['POST','GET'])
def settings():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM settings WHERE username=?""",
                (session['user'],))
    set = cur.fetchall()

    return render_template('settings.html', fontsize=str(set[0][2]), theme=str(set[0][1]))


@app.route('/settings/savetheme', methods=['GET'])
def saveTheme():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    theme = request.args.get('theme', '')
    cur.execute("""UPDATE settings
                    SET theme=?
                    WHERE username=?""", (theme, session['user']))
    con.commit()
    con.close()

    return redirect(url_for('settings'))
    #maybe would be more effiecient without the get method, for example ajax

@app.route('/settings/save-settings', methods=['POST'])
def saveOtherSettings():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""UPDATE settings
                    SET fontsize=?
                    WHERE username=?""", (request.form['fontSize'], session['user']))
    con.commit()
    con.close()

    return redirect(url_for('settings'))



@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/dev_board')
def board():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM messages""")
    set = cur.fetchall()
    return render_template('dev_board_messages.html', messages=set)

@app.route('/interest_test')
def interest_test():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM genres""")
    genres = cur.fetchall()

    for x in range(len(genres)):
        genres[x] = genres[x][0]

    return render_template('interest_test.html', genres=genres)



#INSERTING FUNCTIONS

@app.route('/insert-genres')
def insert_genres():
    genres = ['Horror', 'PsychologicalHorror', 'GoodAtmosphere', 'Survival', 'FPS', 'Fighting', 'SwordFighting', 'SoulsLike', 'Simulator', 'PvP', 'PvE', 'SinglePlayer', 'Coop', 'BattleRoyal',
    'Sports', 'Puzzle', 'FreeToPlay', 'Racing', 'Action', 'Adventure', 'Apocalyptic']
    for x in range(len(genres)):
        con = sqlite3.connect('userdata.db')
        cur = con.cursor()
        cur.execute("""INSERT INTO genres (genre)
                        VALUES (?)""", (genres[x],))
        con.commit()
        con.close()
    return 'all genres are inserted!'




#CREATING TABLES
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




@app.route('/message-table-create')
def message_table_create():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE messages (
        username VARCHAR(15) NOT NULL PRIMARY KEY,
        reason VARCHAR(20),
        text VARCHAR(500)
        )
        """)
    con.commit()
    con.close()
    return 'message tbl created!'




@app.route('/settings-table-create')
def settings_table_create():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE settings
        (
        username VARCHAR(15) NOT NULL PRIMARY KEY,
        theme INTEGER NOT NULL,
        fontsize INTEGER
        )
        """)
    con.commit()
    con.close()
    return 'settings tbl created!'


@app.route('/create-table-genres')
def create_table_genres():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE genres
        (
        genre VARCHAR(20) NOT NULL PRIMARY KEY
        )
        """)
    con.commit()
    con.close()
    return 'genres table is created!'



#SEE FUNCTIONS
@app.route('/see')
def see():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM user;
        """)
    rows = cur.fetchall()
    return str(rows)




@app.route('/see-messages')
def see_messages():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM messages;
        """)
    rows = cur.fetchall()
    return str(rows)




@app.route('/see-settings')
def see_settings():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM settings;
        """)
    rows = cur.fetchall()
    return str(rows)

@app.route('/see-genres')
def see_genres():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM genres;
        """)
    rows = cur.fetchall()
    return str(rows)



#CLEARING FUNCTIONS
@app.route('/clear-messages')
def clear_messages():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                DELETE FROM messages;
        """)
    con.commit()
    con.close()
    return 'messages cleared'




@app.route('/clear-usertable')
def clear_message():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                DELETE FROM user;
        """)
    con.commit()
    con.close()
    return 'users cleared'


@app.route('/clear-sessions')
def clear_sessions():
    session.clear()

    return "cleared"

@app.route('/clear-all')
def clear_all():
    session.clear()
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                DELETE FROM user;
        """)
    con.commit()
    cur.execute("""
                DELETE FROM messages;
        """)
    con.commit()
    cur.execute("""
                DELETE FROM settings;
        """)
    con.commit()
    con.close()
    return "all cleared"



