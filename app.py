from flask import Flask, render_template, request, session, url_for, redirect
app = Flask(__name__)
import sqlite3, requests, json

app.secret_key = 'LOL_SECRET_KEY'

#NOTES
#IF NOT MUCH TIME LEFT AND USING API IS TOO COMPLICATED, INSERT 7-10 GAMES YOURSELF AND WORK WITH IT

#   To do list:
#   Sign out
#   Wishlist
#   Differentiate between developer and user
#   Theme selection
#   Tidy up code




#GLOBAL FUNCTIONS and CLASSES and OTHER VARIABLES

class game_obj:
        def __init__(self, id, title, description, m_score, g_score, tags, genres, r_date, l_date, screenshots, image):
            self.id = id
            self.title = title
            self.description = description
            self.m_score = m_score
            self.g_score = g_score
            self.tags = tags
            self.genres = genres
            self.r_date = r_date
            self.l_date = l_date
            self.screenshots = screenshots
            self.image = image

games = []

def search(name_entered):
    games.clear()

    request_Games = requests.get("https://api.rawg.io/api/games?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100&search=" + name_entered)

    Games_file = request_Games.json()

    for game_result in Games_file['results']:

        request_Game = requests.get("https://api.rawg.io/api/games/"+ str(game_result['id']) +"?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")

        game = request_Game.json()

        genres = []
        tags = []

        for genre in game['genres']:
            genres.append(genre['name'])

        for tag in game['tags']:
            tags.append(tag['name'])

        game['id'] = game_obj(game['id'], game['name'], game['description'], game['metacritic'], game['rating'], tags, genres, game['released'], game['updated'], None, game['background_image'])
        games.append(game['id'])

    return games

def game_more_info(index, games):
    index = int(index)
    game_object = games[index]
    request_Game_screenshots = requests.get("https://api.rawg.io/api/games/"+ str(game_object.id) +"/screenshots?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")
    Screenshot_file = request_Game_screenshots.json()
    screenshots_results = Screenshot_file['results']
    screenshots = []
    for screenshot in screenshots_results:
        screenshots.append(screenshot['image'])
    game_object.screenshots = screenshots

    return game_object









#PAGES

@app.route('/login')
def login_page():
        return render_template('login.html')




@app.route('/sign_up')
def signup_page():
        return render_template('creating_account.html')




@app.route('/signing_up', methods=['GET','POST'])
def signing_up():

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




        cur.execute(""" SELECT tag_name FROM tags """)
        tags = cur.fetchall()

        cur.execute(""" SELECT genre_name FROM genres """)
        genres = cur.fetchall()



        #linking the new user with the existing tags
        for tag in tags:
            cur.execute(""" INSERT INTO userTags (username, tag_name, interest_percent)
                            VALUES (?,?,?)""", (request.form['usern'], tag[0], '0'))
        con.commit()


        #linking the new user with the existing genres

        for genre in genres:
            cur.execute(""" INSERT INTO userGenres (username, genre_name, interest_percent)
                            VALUES (?,?,?)""", (request.form['usern'], genre[0], '0'))
        con.commit()




        session['user'] = request.form['usern']

        return redirect(url_for('interest_test'))



@app.route('/logging_in', methods=['POST'])
def logging_in():
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




@app.route('/')
def home():
    if session.get('user') != None:
        con = sqlite3.connect('userdata.db')
        cur = con.cursor()

        if session.get('user') == None:
            return render_template('home.html', name="Please, sign in!")
        else:
            cur.execute("""SELECT name FROM user WHERE username=?""",
                            (session['user'],))
            name = cur.fetchall()
            if session['user'] == 'albert_dev':
                return render_template('home.html', tool="<a href=dev_board id=board>Dev board</a>",
                                                    name="Welcome, " + name[0][0])
            else:
                return render_template('home.html', name="Welcome, " + name[0][0])
    else:

        return redirect(url_for('login_page'))




@app.route('/tech-support', methods=['GET', 'POST'])
def tech_support():
    if session.get('user') != None:
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
            return render_template('tech-support.html', match=0)

    else:

        return render_template('tech-support.html')




@app.route('/catalogue')
def catalogue():

    return render_template('catalogue.html')

@app.route('/catalogue/search', methods=['GET'])
def catalogue_search():
    name_entered = request.args.get('name', '')
    games = search(name_entered)
    return render_template('catalogue.html', games=games)

@app.route('/game', methods=['GET'])
def game():
        index = request.args.get('index', '')
        game = game_more_info(index, games)
        return render_template('game_page.html', game=game)

# @app.route('/game', methods=['GET'])
# def game():
#     id = request.args.get('id', '')

#     request_Game = requests.get("https://api.rawg.io/api/games/"+ id +"?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")
#     request_Game_screenshots = requests.get("https://api.rawg.io/api/games/"+ id +"/screenshots?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")

#     game = request_Game.json()
#     Screenshots_file = request_Game_screenshots.json()
#     Screenshots_results = Screenshots_file['results']

#     screenshots = []
#     genres = []
#     tags = []
#     current_description = Game_file['description']
#     new_description = ""
#     wrong_strings = ["<p>", "</p>", "<h3>", "</h3>", "&#39;", "<strong>", "</strong>", "<br/>", "<br />", "<br>"]

#     #for loop to go through the api's description and remove the html tags, or to replace it with '
#     for string in wrong_strings:
#         if string != "&#39;":
#             new_description = current_description.replace(string, "")
#             current_description = new_description
#         else:
#             new_description = current_description.replace(string, "'")
#             current_description = new_description


#     for screenshot in Screenshots_results:
#         screenshots.append(screenshot['image'])

#     for genre in game['genres']:
#         genres.append(genre['name'])

#     for tag in game['tags']:
#         tags.append(tag['name'])


#     game = game_obj(game['id'], game['name'], current_description, game['metacritic'], game['rating'], tags, genres, game['released'], game['updated'], screenshots, game['background_image'])

#     return render_template('game_page.html', game=game)


@app.route('/settings', methods=['POST','GET'])
def settings():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM settings WHERE username=?""",
                (session['user'],))
    set = cur.fetchall()

    return render_template('settings.html', fontsize=str(set[0][2]), theme=str(set[0][1]))

@app.route('/sign_out')
def signout():
    session.pop('user', None)
    return redirect(url_for('login_page'))


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


@app.route('/dev_board', methods=['POST'])
def message_board():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()

    cur.execute("""SELECT * FROM messages WHERE reason=?""", ("Bug report",))
    bug_reports = cur.fetchall()

    cur.execute("""SELECT * FROM messages WHERE reason=?""", ("Inconvinience",))
    inconviniences = cur.fetchall()

    cur.execute("""SELECT * FROM messages WHERE reason=?""", ("Suggestion",))
    suggestions = cur.fetchall()

    if request.method == 'POST':

        resolved_messages = request.form.getlist('message')

        for message in resolved_messages:
            cur.execute("""DELETE FROM messages WHERE username=?""", (message,))
            con.commit()


    return render_template('dev_board_messages.html', bug_reports=bug_reports, inconviniences=inconviniences, suggestions=suggestions)
















@app.route('/interest_test')
def interest_test():

    request_genres = requests.get("https://api.rawg.io/api/genres?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")
    request_tags = requests.get("https://api.rawg.io/api/tags?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")

    genres_file = request_genres.json()
    genres = [None] * len(genres_file['results'])

    tags_file = request_tags.json()
    tags = [None] * len(tags_file['results'])


    for x in range(len(genres_file['results'])):
        genres[x] = genres_file['results'][x]['name']
    for x in range(len(tags_file['results'])):
        tags[x] = tags_file['results'][x]['name']

    return render_template('interest_test.html', genres=genres, tags=tags)

@app.route('/save_genres', methods=['POST'])
def save_gernes():
    genres = request.form.getlist('genre')
    tags = request.form.getlist('tag')





@app.route('/test_home')
def test_home():

    request_racingGames = requests.get("https://api.rawg.io/api/games?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100&genres=racing")

    racingGames_file = request_racingGames.json()

    class game_obj:
        def __init__(self, title, image):
            self.title = title
            self.image = image

    games = []


    for game in racingGames_file['results']:

        game['id'] = game_obj(game['name'], game['background_image'])
        games.append(game['id'])



    return render_template('test_home.html', games=games)



#INSERTING FUNCTIONS

@app.route('/insert_genres')
def insert_genres():
    request_genres = requests.get("https://api.rawg.io/api/genres?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")
    genres_file = request_genres.json()

    genres = []

    for genre in genres_file['results']:
        genres.append(genre['name'])

    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    for genre in genres:
        cur.execute("""
        INSERT INTO genres (genre_name)
        VALUES (?)""", (genre,)
        )
        con.commit()

    con.close()

    return 'all genres are inserted!'

@app.route('/insert_tags')
def insert_tags():
    request_tags = requests.get("https://api.rawg.io/api/tags?key=fe9de1fd1c1f4b078881a31bb2971169&page_size=100")
    tags_file = request_tags.json()

    tags = []

    for tag in tags_file['results']:
        tags.append(tag['name'])

    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    for tag in tags:
        cur.execute("""
        INSERT INTO tags (tag_name)
        VALUES (?)""", (tag,)
        )
        con.commit()

    con.close()

    return 'all tags are inserted!'




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



@app.route('/create_genres_table')
def create_genres_table():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE genres
        (
            genre_name VARCHAR(15) NOT NULL PRIMARY KEY
        )
        """)
    con.commit()
    con.close()
    return 'genres tbl created'

@app.route('/create_tags_table')
def create_tags_table():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE tags
        (
            tag_name VARCHAR(15) NOT NULL PRIMARY KEY
        )
        """)
    con.commit()
    con.close()
    return 'tags tbl created'

@app.route('/create_userTags_table')
def create_userTags_table():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
            CREATE TABLE userTags
            (
            username VARCHAR(15) NOT NULL,
            tag_name VARCHAR(15) NOT NULL,
            interest_percent FLOAT NOT NULL,
            FOREIGN KEY(username) REFERENCES user(username),
            FOREIGN KEY(tag_name) REFERENCES tags(tag_name),
            PRIMARY KEY(username, tag_name)
            )
            """)
    con.commit()
    con.close()
    return 'userTags table created!!!'



@app.route('/create_userGenres_table')
def create_userGenres_table():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
            CREATE TABLE userGenres
            (
            username VARCHAR(15) NOT NULL,
            genre_name VARCHAR(15) NOT NULL,
            interest_percent FLOAT NOT NULL,
            FOREIGN KEY(username) REFERENCES user(username),
            FOREIGN KEY(genre_name) REFERENCES tags(genre_name),
            PRIMARY KEY(username, genre_name)
            )
            """)
    con.commit()
    con.close()
    return 'userGenres table created!!!'



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

@app.route('/see-tags')
def see_tags():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT tag_name FROM tags;
        """)
    rows = cur.fetchall()
    return str(rows)

@app.route('/see-userTags')
def see_userTags():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM userTags;
        """)
    rows = cur.fetchall()
    return str(rows)

@app.route('/see-userGenres')
def see_userGenres():
    con = sqlite3.connect('userdata.db')
    cur = con.cursor()
    cur.execute("""
                SELECT * FROM userGenres;
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
                DELETE FROM user
        """)
    cur.execute("""
                DELETE FROM messages
        """)
    cur.execute("""
                DELETE FROM settings
        """)
    cur.execute("""
                DELETE FROM userTags
        """)
    cur.execute("""
                DELETE FROM userGenres
        """)


    con.commit()
    con.close()
    return "all cleared"


