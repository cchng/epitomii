

import markdown
import os
import sqlite3
import urlparse
from datetime import datetime, timedelta
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, make_response, Markup
from flask_mail import Mail, Message
#import smtplib
#from email.mime.text import MIMEText


YOUTUBE_CODE = "opeETnB8m8w"
DAILY_JAM = "https://www.youtube.com/embed/{code}?rel=0&amp;controls=0&amp;showinfo=0;autoplay=1&loop=1&playlist={code}".format(code=YOUTUBE_CODE)
#DAILY_JAM = "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/244976490&amp;auto_play=true&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false&amp;visual=true"

POST_PATH = "_posts/behind-the-scenes2.md"
POST_TITLE = "102 / BEHIND THE SCENES"

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'epitomii.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = os.environ.get("GMAIL_SMTP_USER"),
    MAIL_PASSWORD = os.environ.get("GMAIL_SMTP_PASSWORD")
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')
def index():
  #  username = request.cookies.get('username')
    return render_template('index.html', jam=DAILY_JAM, show_video=True)

@app.route('/music')
def music():
  
    db = get_db()
    cur = db.execute('select url from jams order by id desc')
    jams = cur.fetchall()
    return render_template('music.html', jams=jams)

@app.route('/posts')
def posts():
    db = get_db()
    cur = db.execute('select title, filepath from posts order by id desc')
    posts = cur.fetchall()
    return render_template('posts.html', posts=posts)

@app.route('/show_post', methods=["POSTp"])
def show_post():
    with open(request.data, "r") as md:
        print request.data
        content = md.read()
        
    return Markup(markdown.markdown(content))
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


@app.cli.command('add-jam')
def add_jam():
    db = get_db()
    if "soundcloud" in DAILY_JAM:
        entry = DAILY_JAM.replace("auto_play=true", "auto_play=false")
    else:
        entry = DAILY_JAM.split("?")[0]
        
    db.execute('insert into jams (url) values (?)', [entry])
    db.commit()
    print('{} was successfully posted'.format(entry))

@app.cli.command('add-post')
def add_post():
    path = POST_PATH
    title = POST_TITLE
    db = get_db()
    db.execute('insert into posts (title, filepath) values (?, ?)',
               [title, path])
    db.commit()
    print('{} {} was successfully posted'.format(path, title))

@app.cli.command("rm-jam")
def remove_entry():
    db = get_db()
    if "soundcloud" in DAILY_JAM:
        entry = DAILY_JAM.replace("auto_play=true", "auto_play=false")
    else:
        entry = DAILY_JAM.split("?")[0]

    db.execute("delete from jams where url=(?)", [entry])
    db.commit()
    print("latest entry deleted")

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

        
# a route for generating sitemap.xml
@app.route('/sitemap.xml', methods=['GET'])        
def sitemap():
    """Generate sitemap.xml 

    References: 

    	- http://fan-zf.blogspot.my/2013/07/generate-sitemap-using-flask.html
    	- http://flask.pocoo.org/snippets/108/
    """
    pages = []

    thirty_days_ago=datetime.now() - timedelta(days=30)
    url_root = request.url_root[:-1]
    print url_root
    # static pages
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments)==0:
            pages.append(
                [urlparse.urljoin(url_root, rule.rule), thirty_days_ago]
            )

    print(pages)
    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/send_email', methods=["POST"])
def send_email():
    data = request.data
    print(data)
    if request.method=="POST":
        name = request.form["name"]
        msg = request.form["msg"]
        sender = request.form["sender"]
        recipient = [app.config["MAIL_USERNAME"]]
        phone = request.form["phone"]
        
        if not sender:
            print("sender: {}".format(sender))
            sender=app.config["MAIL_USERNAME"]
            
        if not name:
            name="anon"
            
        subject = "[epitomii] message from {}".format(name)
        
        mail = Mail(app)
        message = Message(subject,
                          sender=sender,
                          recipients=recipient)
        message.body = msg + "\n\nemail: {}".format(sender)

        if phone:
            message.body += "\nphone: {}".format(phone)
        
        mail.send(message)

    return '', 204

    
if __name__ == "__main__":
    app.run()

