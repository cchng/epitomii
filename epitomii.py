import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, make_response


YOUTUBE_CODE = "bo9YNgdMpkQ"
DAILY_JAM = "https://www.youtube.com/embed/{code}?rel=0&amp;controls=0&amp;showinfo=0;autoplay=1&loop=1&playlist={code}".format(code=YOUTUBE_CODE)

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'jams.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def index():
  #  username = request.cookies.get('username')
    return render_template('index.html', jam=DAILY_JAM)

@app.route('/music')
def music():
  
    db = get_db()
    cur = db.execute('select url from entries order by id desc')
    jams = cur.fetchall()
    print(jams)
#    return ",".join(jams)
    return render_template('music.html', jams=jams)

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/hello')
# @app.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', name=name)

# @app.route('/projects/')
# def projects():
#     return 'The project page'

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/contact')
# def contact():
#     return render_template('contact.html')

# # @app.route('/user/<username>')
# # def show_user_profile(username='Stranger'):
# #     # show the user profile for that user
# #     return 'User %s' % username

# # @app.route('/blankpage')
# # def blank_page():
# #     return render_template('blank-page.html')


# @app.route('/forms')
# def forms():
#     return "forms"
# # #     return render_template('forms.html')

# # @app.route('/post/<int:post_id>')
# # def show_post(post_id):
# #     # show the post with the given id, the id is an integer
# #     return 'Post %d' % post_id


# # @app.errorhandler(404)
# # def not_found(error):
# #     resp = make_response(render_template('error.html'), 404)
# #     resp.headers['X-Something'] = 'A value'
# #     return resp

# # @app.route('/login', methods=['GET', 'POST'])
# # def login():
# #     error = None
# #     if request.method == 'POST':
# #         if request.form['username'] != app.config['USERNAME']:
# #             error = 'Invalid username'
# #         elif request.form['password'] != app.config['PASSWORD']:
# #             error = 'Invalid password'
# #         else:
# #             session['logged_in'] = True
# #             flash('You were logged in')
# #             return redirect(url_for('show_entries'))
# #     return render_template('login.html', error=error)

# # @app.route('/logout')
# # def logout():
# #     session.pop('logged_in', None)
# #     flash('You were logged out')
# #     return redirect(url_for('show_entries'))

# # @app.route('/')
# # def show_entries():
# #     db = get_db()
# #     cur = db.execute('select title, text from entries order by id desc')
# #     entries = cur.fetchall()
# #     return render_template('show_entries.html', entries=entries)

#@app.route('/add', methods=['POST'])
@app.cli.command('add')
def add_entry():
    db = get_db()

    db.execute('insert into entries (url) values (?)',
                 [DAILY_JAM.split("?")[0]])
    db.commit()
    print('New entry was successfully posted')
  
# #     flash('New entry was successfully posted')
# #     return redirect(url_for('show_entries'))

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'
    
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()




if __name__ == "__main__":
    app.run()
